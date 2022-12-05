using System.Collections.Generic;
using System.Linq;
using Unity.MLAgents;
using Unity.MLAgents.Actuators;
using Unity.MLAgents.Policies;
using Unity.MLAgents.Sensors;
using UnityEngine;

public class Test : Agent
{
    public enum Movement
    {
        NSWE,
        ForwardAndRotate,
        DiscreteActions
    }

    public enum Communication
    {
        Absent,
        Distance,
        FreeCommunication,
        TargetPosition
    }

    private List<string> commList;
    public List<Communication> CommunicationMode;
    public Movement movementMode;
    public float playerSpeed = 10;
    public float rotationSensitivity = 10;
    public bool ownPositionAsObservation;

    [Header("Rewards")]
    public float existenctialPenalty = 0.001f;

    [Tooltip("The penalty is multiplied by 1/distance from the near agent if they are on sigth")]
    public float nearAgentPenalty = 0.1f;

    public float hitWallPenalty = 0.05f;
    public float hitAgentPenalty = 0.03f;

    public float checkpointReward = 0.15f;
    public float targetReward = 1;
    public float nearTargetReward = 0.01f;

    private Dictionary<string, float> communicationMap;

    private Transform Swarm;
    private List<Test> otherAgents;
    private Transform Target;

    private CharacterController controller;
    private List<Checkpoint> clearedCheckpoints;
    private Vector3 initialPosition;

    [Header("Test parameters")]
    public List<Vector3> TargetPositions;
    private int testNumber = 0;
    private System.DateTime startTime;
    public int maxMoves;
    private int moves = 0;
    private float totalReward;

    void Start()
    {
        commList = new List<string>();
        controller = GetComponent<CharacterController>();
        clearedCheckpoints = new List<Checkpoint>();

        Swarm = transform.parent;
        initialPosition = transform.localPosition;
        Transform Goal = Swarm.parent.Find("GOAL");
        Target = Goal.Find("Target");

        otherAgents = new List<Test>(Swarm.GetComponentsInChildren<Test>());
        otherAgents.Remove(this);

        int obsSize = 0;
        communicationMap = new Dictionary<string, float>();
        //Initialize the communication data structure
        if (CommunicationMode.Contains(Communication.Distance))
        {
            obsSize += otherAgents.Count;
            foreach (var agent in otherAgents)
                communicationMap.Add(agent.name + "distance", 0);
        }
        if (CommunicationMode.Contains(Communication.FreeCommunication))
        {
            obsSize += otherAgents.Count;
            foreach (var agent in otherAgents)
                communicationMap.Add(agent.name + "freeCommunication", 0);
        }
        if (CommunicationMode.Contains(Communication.TargetPosition))
        {
            obsSize += 2;
            communicationMap.Add("targetx", 0);
            communicationMap.Add("targetz", 0);
        }

        if (ownPositionAsObservation)
            obsSize += 2;

        // Since I can't set the size from here I just notify the user
        Debug.Assert(GetComponent<BehaviorParameters>().BrainParameters.VectorObservationSize == obsSize,
        "Wrong observation size, change it from the prefab of the Agent. Actual value = " +
        GetComponent<BehaviorParameters>().BrainParameters.VectorObservationSize + " but expected " + obsSize +
        "\nRemember you have Communication set to " + CommunicationMode.ToString());


        startTime = System.DateTime.UtcNow;
        moves = 0;
        totalReward = 0;
    }

    private new void AddReward(float reward)
    {
        totalReward += reward;
        base.AddReward(reward);
    }

    public void Checkpoint(Checkpoint cp)
    {
        AddReward(checkpointReward);
        clearedCheckpoints.Add(cp);
    }

    void OnCollisionEnter(Collision collision)
    {
        GameObject go = collision.gameObject;

        if (go.CompareTag("wall"))
            AddReward(-hitWallPenalty);
        // Hit with another agent
        else if (go.CompareTag("agent") && !go.Equals(gameObject))
            AddReward(-hitAgentPenalty);
    }

    public override void OnEpisodeBegin()
    {
        foreach (Checkpoint cp in clearedCheckpoints)
            cp.SetActive(true);

        clearedCheckpoints.Clear();

        ResetPosition();
        testNumber++;

        if (testNumber - 1 == TargetPositions.Count)
        {
            Application.Quit();
            // UnityEditor.EditorApplication.isPlaying = false;
        }

        startTime = System.DateTime.UtcNow;
        moves = 0;
    }

    private void ResetPosition()
    {
        transform.localPosition = initialPosition;
    }

    private void MoveTarget()
    {
        // Move the target to a new spot
        if (testNumber - 1 < TargetPositions.Count)
            Target.localPosition = TargetPositions[testNumber - 1];
        reachedGoal = false;
    }

    public void Communicate(string id, float message)
    {
        communicationMap[id] = message;
    }

    public override void CollectObservations(VectorSensor sensor)
    {

        if (CommunicationMode.Contains(Communication.Distance))
            CheckNearAgentsAndUpdateCommunication();
        else
            CheckNearAgents();

        //The only observation is the raycast if communication is not used
        if (CommunicationMode.Count() != 0 && !CommunicationMode.Contains(Communication.Absent))
            sensor.AddObservation(communicationMap.Values.ToList());

        if (ownPositionAsObservation)
        {
            sensor.AddObservation(transform.localPosition.x);
            sensor.AddObservation(transform.localPosition.z);
        }

    }

    private bool reachedGoal;
    public void ReachGoal() { reachedGoal = true; }
    private void CommunicateTargetPosition()
    {
        foreach (Test agent in otherAgents)
        {
            agent.Communicate("targetx", Target.localPosition.x);
            agent.Communicate("targetz", Target.localPosition.z);
        }
    }
    public override void OnActionReceived(ActionBuffers actionBuffers)
    {
        switch (movementMode)
        {
            case Movement.NSWE:
                Vector3 direction = Vector3.zero;
                direction.x = actionBuffers.ContinuousActions[0];
                direction.z = actionBuffers.ContinuousActions[1];

                controller.Move(playerSpeed * Time.deltaTime * direction);
                if (direction != Vector3.zero)
                    transform.forward = direction;
                break;

            case Movement.ForwardAndRotate:
                var rotation = actionBuffers.ContinuousActions[0];
                var forwardMovement = actionBuffers.ContinuousActions[1];

                controller.Move(forwardMovement * playerSpeed * Time.deltaTime * transform.forward);
                transform.Rotate(rotation * rotationSensitivity * Vector3.up);
                break;

            case Movement.DiscreteActions:
                var dirToGo = Vector3.zero;
                var rotateDir = Vector3.zero;

                var action = actionBuffers.DiscreteActions[0];

                switch (action)
                {
                    case (int)DiscreteCommands.Forward:
                        dirToGo = transform.forward * 1f;
                        break;
                    case (int)DiscreteCommands.Backward:
                        dirToGo = transform.forward * -1f;
                        break;
                    case (int)DiscreteCommands.TurnLeft:
                        rotateDir = transform.up * 1f;
                        break;
                    case (int)DiscreteCommands.TurnRight:
                        rotateDir = transform.up * -1f;
                        break;
                    case (int)DiscreteCommands.Left:
                        dirToGo = transform.right * -0.75f;
                        break;
                    case (int)DiscreteCommands.Right:
                        dirToGo = transform.right * 0.75f;
                        break;
                }
                transform.Rotate(rotateDir * rotationSensitivity);
                controller.Move(playerSpeed * Time.deltaTime * dirToGo);
                break;
        }

        if (reachedGoal)
        {
            Debug.Log("Reached Target in test number " + testNumber);
            System.TimeSpan ts = System.DateTime.UtcNow - startTime;
            Debug.Log("Time needed to reach: " + (ts.TotalMilliseconds / 1000.0f).ToString() + "  ---  Total reward = " + totalReward);
            System.IO.File.WriteAllLines("Communication_"+name+".txt", commList);
            ReachedTarget();
            return;
        }

        AddReward(-existenctialPenalty);

        CheckTargetProximity();

        moves++;
        if (moves >= maxMoves)
        {
            System.TimeSpan ts = System.DateTime.UtcNow - startTime;
            Debug.Log("Failed test number " + testNumber + " after " + (ts.TotalMilliseconds / 1000.0f).ToString() + " seconds" + "  ---  Total reward = " + totalReward);
            ReachedTarget();
            return;
        }

        if (CommunicationMode.Contains(Communication.FreeCommunication))
        {
            int messageIndex = actionBuffers.ContinuousActions.Length - 1;
            float message = actionBuffers.ContinuousActions[messageIndex];
            commList.Add(message.ToString());
            foreach (Test agent in otherAgents)
            {
                agent.Communicate(name + "freeCommunication", message);
            }
        }

    }

    private void CheckTargetProximity()
    {
        Vector3 dir = (Target.position - transform.position).normalized;
        if (Physics.Raycast(transform.position, dir, out RaycastHit hit))
            if (hit.collider.name.Equals(Target.name))
            {
                AddReward((1 / hit.distance) * nearTargetReward);
                if (CommunicationMode.Contains(Communication.TargetPosition))
                    CommunicateTargetPosition();
            }
    }

    // Set the reward of all agents to 1, End the episode and move the target
    private void ReachedTarget()
    {
        SetReward(targetReward);
        EndEpisode();
        foreach (Test agent in otherAgents)
        {
            agent.SetReward(targetReward);
            agent.EndEpisode();
        }

        MoveTarget();
    }

    // If the agents are on sigth add the negative reward, otherwise 0,
    private void CheckNearAgents()
    {
        Vector3 dir;
        foreach (Agent agent in otherAgents)
        {
            dir = (agent.transform.position - transform.position).normalized;
            if (Physics.Raycast(transform.position, dir, out RaycastHit hit))
                if (hit.collider.name.Equals(agent.name))
                    AddReward(-(1 / hit.distance) * nearAgentPenalty);
        }
    }

    // Near agent penalty and update communicationList
    private void CheckNearAgentsAndUpdateCommunication()
    {
        Vector3 dir;
        foreach (Agent agent in otherAgents)
        {
            dir = (agent.transform.position - transform.position).normalized;
            if (Physics.Raycast(transform.position, dir, out RaycastHit hit))
            {
                if (hit.collider.name.Equals(agent.name))
                {
                    AddReward(-(1 / hit.distance) * nearAgentPenalty);
                    communicationMap[agent.name + "distance"] = hit.distance;
                }
                else
                    communicationMap[agent.name + "distance"] = 0;
            }
        }
    }

    public override void Heuristic(in ActionBuffers actionsOut)
    {
        var discreteActionsOut = actionsOut.DiscreteActions;
        var continuousActionsOut = actionsOut.ContinuousActions;
        switch (movementMode)
        {
            case Movement.DiscreteActions:
                if (Input.GetKey(KeyCode.D))
                    discreteActionsOut[0] = (int)DiscreteCommands.Right;
                else if (Input.GetKey(KeyCode.W))
                    discreteActionsOut[0] = (int)DiscreteCommands.Forward;
                else if (Input.GetKey(KeyCode.A))
                    discreteActionsOut[0] = (int)DiscreteCommands.Left;
                else if (Input.GetKey(KeyCode.S))
                    discreteActionsOut[0] = (int)DiscreteCommands.Backward;
                break;

            default:
                continuousActionsOut = actionsOut.ContinuousActions;
                continuousActionsOut[0] = Input.GetAxis("Horizontal");
                continuousActionsOut[1] = Input.GetAxis("Vertical");
                break;
        }

        if (CommunicationMode.Contains(Communication.FreeCommunication))
            continuousActionsOut[continuousActionsOut.Length - 1] = 0;
    }
}