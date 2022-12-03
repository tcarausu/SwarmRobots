using System.Collections.Generic;
using System.Linq;
using Unity.MLAgents;
using Unity.MLAgents.Actuators;
using Unity.MLAgents.Policies;
using Unity.MLAgents.Sensors;
using UnityEngine;

enum DiscreteCommands
{
    None,
    Forward,
    Backward,
    TurnLeft,
    TurnRight,
    Left,
    Right,
}

public class WalkerAgentMulti : Agent
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

    public Communication CommunicationMode;
    public Movement movementMode;
    public float playerSpeed = 10;
    public float rotationSensitivity = 10;

    public float existenctialPenalty = 0.001f;

    [Tooltip("The penalty is multiplied by 1/distance from the near agent if they are on sigth")]
    [Header("Inversely proportional to distance")]
    public float nearAgentPenalty = 0.1f;

    public float hitWallPenalty = 0.05f;
    public float hitAgentPenalty = 0.03f;

    public float checkpointReward = 0.15f;
    public float targetReward = 1;
    public float nearTargetReward = 0.01f;

    private Dictionary<string, float> communicationMap;

    private Transform Swarm;
    private List<WalkerAgentMulti> otherAgents;
    private Transform Target;
    private SpawnAreas TargetSpawnAreas;

    private int numTargetsFound = 0;
    [Tooltip("This number represents the number of episodes that the target mantain his starting position")]
    public int firstChangeTargetPos = 10;

    private CharacterController controller;

    private List<Checkpoint> clearedCheckpoints;

    private Transform MySpawnArea;
    private SpawnCheck spawnCheck;
    private Vector3 initialPosition;
    private Vector3 spawnSize;
    private float length; // Since the agent is a cube edge length on the x is supposed to be length on y and z too

    public GameObject usableTrainingArea;
    private Transform _activeMaze;
    private Transform Goal;

    public bool hasRandomMaze;

    void Start()
    {
        controller = GetComponent<CharacterController>();
        clearedCheckpoints = new List<Checkpoint>();

        Swarm = transform.parent;
        spawnCheck = Swarm.gameObject.GetComponent<SpawnCheck>();
        MySpawnArea = Swarm.Find("SpawnArea");
        initialPosition = transform.localPosition;
        spawnSize = MySpawnArea.GetComponent<Renderer>().bounds.size;
        length = GetComponent<BoxCollider>().size.x;
        spawnSize.x -= length / 2;
        spawnSize.z -= length / 2;

        if (hasRandomMaze)
        {
            //getting the objectList of Mazes
            _activeMaze = usableTrainingArea.GetComponent<SelectRandomMaze>().getActiveMaze();
            Goal = _activeMaze.Find("GOAL");
        }
        else
            Goal = usableTrainingArea.transform.Find("GOAL");

        TargetSpawnAreas = Goal.Find("SpawnAreas").gameObject.GetComponent<SpawnAreas>();
        Target = Goal.Find("Target");

        otherAgents = new List<WalkerAgentMulti>(Swarm.GetComponentsInChildren<WalkerAgentMulti>());
        otherAgents.Remove(this);

        int obsSize = 0;
        //Initialize the communication data structure
        if (CommunicationMode.Equals(Communication.Distance) || CommunicationMode.Equals(Communication.FreeCommunication))
        {
            obsSize = otherAgents.Count;
            communicationMap = new Dictionary<string, float>();
            foreach (var agent in otherAgents)
                communicationMap.Add(agent.name, 0);
        }
        else if (CommunicationMode.Equals(Communication.TargetPosition))
        {
            obsSize = 2;
            communicationMap = new Dictionary<string, float>
            {
                { "targetx", 0 },
                { "targety", 0 }
            };
        }

        // Since I can't set the size from here I just notify the user
        Debug.Assert(GetComponent<BehaviorParameters>().BrainParameters.VectorObservationSize == obsSize,
        "Wrong observation size, change it from the prefab of the Agent. Actual value = " +
        GetComponent<BehaviorParameters>().BrainParameters.VectorObservationSize + " but expected " + obsSize +
        "\nRemember you have Communication set to " + CommunicationMode.ToString());
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
        RndSpawn();
    }

    private void RndSpawn()
    {
        Vector3 rndPosition;
        do
        {
            rndPosition = new Vector3(
                Random.value * spawnSize.x - spawnSize.x / 2,
                initialPosition.y,
                Random.value * spawnSize.z - spawnSize.z / 2);
        } while (!spawnCheck.IsSafePosition(rndPosition, length));

        transform.localPosition = rndPosition;
    }

    private void MoveTarget()
    {
        Target.localPosition = TargetSpawnAreas.GetRndPosition();
    }

    public void Communicate(string agentName, float message)
    {
        communicationMap[agentName] = message;
    }

    public override void CollectObservations(VectorSensor sensor)
    {
        if (CommunicationMode.Equals(Communication.Distance))
            CheckNearAgentsAndUpdateCommunication();
        else
            CheckNearAgents();

        //The only observation is the raycast if communication is not used
        if (!CommunicationMode.Equals(Communication.Absent))
            sensor.AddObservation(communicationMap.Values.ToList());
    }

    private void CommunicateTargetPosition()
    {
        foreach (WalkerAgentMulti agent in otherAgents)
        {
            agent.Communicate("targetx", Target.localPosition.x);
            agent.Communicate("targetz", Target.localPosition.z);
        }
    }

    private bool reachedGoal;

    public void ReachGoal()
    {
        reachedGoal = true;
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
            ReachedTarget();
            return;
        }

        AddReward(-existenctialPenalty);

        CheckTargetProximity();

        if (CommunicationMode.Equals(Communication.FreeCommunication))
        {
            int messageIndex = actionBuffers.ContinuousActions.Length - 1;
            foreach (WalkerAgentMulti agent in otherAgents)
            {
                float message = actionBuffers.ContinuousActions[messageIndex];
                agent.Communicate(name, message);
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
                if (CommunicationMode.Equals(Communication.TargetPosition))
                    CommunicateTargetPosition();
            }
    }

    // Set the reward of all agents to 1, End the episode and move the target
    private void ReachedTarget()
    {
        SetReward(targetReward);
        EndEpisode();
        numTargetsFound++;

        foreach (WalkerAgentMulti agent in otherAgents)
        {
            agent.numTargetsFound++;
            agent.SetReward(targetReward);
            agent.EndEpisode();
        }

        reachedGoal = false;

        // Radomize the maze and target only after "firstChangeTargetPos" number of episodes
        if (numTargetsFound < firstChangeTargetPos)
            return;

        if (hasRandomMaze)
        {
            _activeMaze = usableTrainingArea.GetComponent<SelectRandomMaze>().getActiveMaze();
            Goal = _activeMaze.Find("GOAL");
            TargetSpawnAreas = Goal.Find("SpawnAreas").gameObject.GetComponent<SpawnAreas>();
            Target = Goal.Find("Target");
        }

        MoveTarget();
    }

    // If the agents are on sigth add the negative reward, otherwise 0,
    private void CheckNearAgents()
    {
        Vector3 dir;
        foreach (WalkerAgentMulti agent in otherAgents)
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
                    communicationMap[agent.name] = hit.distance;
                }
                else
                    communicationMap[agent.name] = 0;
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



        if (CommunicationMode.Equals(Communication.FreeCommunication))
            continuousActionsOut[continuousActionsOut.Length-1] = 0;
    }
}