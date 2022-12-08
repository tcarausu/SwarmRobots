using System.Collections.Generic;
using System.IO;
using System.Linq;
using Unity.MLAgents;
using Unity.MLAgents.Actuators;
using Unity.MLAgents.Policies;
using Unity.MLAgents.Sensors;
using UnityEngine;

struct AgentDistance
{
    public Test agent;
    public float distance;

    public AgentDistance(Test agent, float distance) : this()
    {
        this.agent = agent;
        this.distance = distance;
    }
    public void SetDistanceFrom(Vector3 point) { this.distance = Vector3.Distance(agent.transform.localPosition, point); }
}

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
        Position
    }

    public string CommToString(Communication comm)
    {
        return comm switch
        {
            Communication.Absent => "",
            Communication.Distance => "Distance",
            Communication.FreeCommunication => "Free",
            Communication.Position => "Position",
            _ => "",
        };
    }

    private List<string> commList;

    public List<Communication> CommunicationMode;
    public Movement movementMode;
    public float playerSpeed = 10;
    public float rotationSensitivity = 10;

    [Header("Rewards")]
    public float existenctialPenalty = 0.001f;

    [Tooltip("The penalty is multiplied by 1/distance from the near agent if they are on sigth")]
    public float nearAgentPenalty = 0.1f;

    public float hitWallPenalty = 0.05f;
    public float hitAgentPenalty = 0.03f;

    public float checkpointReward = 0.15f;
    public float targetReward = 1;
    public float nearTargetReward = 0.01f;

    public string modelName = "";

    private bool reachedGoal;

    private Dictionary<string, float> communicationMap;
    private readonly int CommunicationSpots = 3;
    private float LastFreeComm = 0;


    private Transform Swarm;
    private List<Test> otherAgents;
    private List<AgentDistance> otherAgentsDistance;
    private Transform Target;

    private CharacterController controller;
    private List<Checkpoint> clearedCheckpoints;
    private Vector3 initialPosition;

    private TargetTestScript targetComponent;

    [Header("Test parameters")]

    private int testNumber = 0;
    private System.DateTime startTime;
    public int maxMoves;
    private int moves = 0;
    private float totalReward;
    private int numAgents;

    private ExplorationCheckpointsController expCheckController;

    new void Awake()
    {
        base.Awake();
        commList = new List<string>();
        controller = GetComponent<CharacterController>();
        clearedCheckpoints = new List<Checkpoint>();

        InitSwarmVariables();

        Transform Goal = Swarm.parent.Find("GOAL");
        Target = Goal.Find("Target");

        targetComponent = Target.GetComponent<TargetTestScript>();
        Transform tExploCheckpoints = Swarm.parent.Find("ExplorationCheckpoints");
        expCheckController = tExploCheckpoints.gameObject.GetComponent<ExplorationCheckpointsController>();

        Debug.Log(expCheckController);

        int obsSize = 0;
        communicationMap = new Dictionary<string, float>();
        //Initialize the communication data structure
        if (CommunicationMode.Contains(Communication.Distance))
        {
            obsSize += CommunicationSpots;
            for (int i = 0; i < CommunicationSpots; i++)
                communicationMap.Add(i + "distance", -1);
        }

        if (CommunicationMode.Contains(Communication.FreeCommunication))
        {
            obsSize += CommunicationSpots;
            for (int i = 0; i < CommunicationSpots; i++)
                communicationMap.Add(i + "freeCommunication", 0);
        }
        if (CommunicationMode.Contains(Communication.Position))
        {
            //My position
            obsSize += 2;
            communicationMap.Add("My_position_x", 0);
            communicationMap.Add("My_position_z", 0);

            obsSize += 2 * CommunicationSpots;
            for (int i = 0; i < CommunicationSpots; i++)
            {
                communicationMap.Add(i + "position_x", 0);
                communicationMap.Add(i + "position_z", 0);
            }
        }

        // Since I can't set the size from here I just notify the user
        Debug.Assert(GetComponent<BehaviorParameters>().BrainParameters.VectorObservationSize == obsSize,
        "Wrong observation size, change it from the prefab of the Agent. Actual value = " +
        GetComponent<BehaviorParameters>().BrainParameters.VectorObservationSize + " but expected " + obsSize +
        "\nRemember you have Communication set to " + CommunicationMode.ToString());

        startTime = System.DateTime.UtcNow;
        moves = 0;
        totalReward = 0;

        CommunicationMode.Sort((x, y) => CommToString(x).CompareTo(CommToString(y)));
        InitModelName();

        
    }

    private void InitSwarmVariables()
    {
        Swarm = transform.parent;
        numAgents = Swarm.childCount - 1;

        var oldSwarm = Swarm.parent.Find("Swarm(" + (numAgents - 4) + ")");
        if (oldSwarm != null)
            oldSwarm.gameObject.SetActive(false);

        initialPosition = transform.localPosition;

        otherAgents = new List<Test>(Swarm.GetComponentsInChildren<Test>());
        otherAgents.Remove(this);
        otherAgentsDistance = new List<AgentDistance>();
        foreach (var agent in otherAgents)
            otherAgentsDistance.Add(new AgentDistance(agent, 0));
    }

    private void InitModelName()
    {
        
        modelName = numAgents + "Agents";
        foreach (Communication comm in CommunicationMode)
        {
            modelName += CommToString(comm);
        }

        targetComponent.initDirectory(modelName);
        expCheckController.initDirectory(modelName);
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
        testNumber++; //starts from 1

        //true when we have gone through all target positions. -1 is needed since testNumber starts from 1
        if (testNumber - 1 == targetComponent.getTotalPositions())  
        {
            
            if (numAgents == 20)
            {
                Application.Quit();
                UnityEditor.EditorApplication.isPlaying = false;
            }
            else
            {
                if (Swarm.gameObject.activeSelf)
                {
                    var nextSwarm = Swarm.parent.Find("Swarm(" + (numAgents + 4) + ")");
                    if (nextSwarm != null && !nextSwarm.gameObject.activeSelf)
                        nextSwarm.gameObject.SetActive(true);
                }
            }
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
        if (testNumber - 1 < targetComponent.getTotalPositions()) { 
            Target.localPosition = targetComponent.getTargetPosition();
        }
        else
        {

            
            //print to file time values. Called here so that just 1 agents calls it
            targetComponent.saveTimeToTarget(modelName);
            Target.localPosition = targetComponent.getTargetPosition();
        }
       
        reachedGoal = false;
    }

    public float AskForFreeCommunication()
    {
        return LastFreeComm;
    }

    public override void CollectObservations(VectorSensor sensor)
    {
        ComputeDistances();
        otherAgentsDistance.Sort((x, y) => x.distance.CompareTo(y.distance));

        CheckNearAgents();

        if (CommunicationMode.Contains(Communication.Distance))
            for(int i = 0; i < CommunicationSpots; i++)
                communicationMap[i + "distance"] = otherAgentsDistance[i].distance;
            

        if (CommunicationMode.Contains(Communication.Position))
        {
            communicationMap["My_position_x"] = transform.localPosition.x;
            communicationMap["My_position_z"] = transform.localPosition.z;

            for (int i = 0; i < CommunicationSpots; i++)
            {
                communicationMap[i + "position_x"] = otherAgentsDistance[i].agent.transform.localPosition.x;
                communicationMap[i + "position_z"] = otherAgentsDistance[i].agent.transform.localPosition.z;
            }

        }

        if (CommunicationMode.Contains(Communication.FreeCommunication))
            for (int i = 0; i < CommunicationSpots; i++)
                communicationMap[i + "freeCommunication"] = otherAgents[i].AskForFreeCommunication();
            

        //The only observation is the raycast if communication is not used
        if (CommunicationMode.Count() != 0 && !CommunicationMode.Contains(Communication.Absent))
            sensor.AddObservation(communicationMap.Values.ToList());

    }

    private void ComputeDistances()
    {
        foreach (var agent in otherAgentsDistance)
            agent.SetDistanceFrom(transform.localPosition);
    }

    public void ReachGoal() { reachedGoal = true; }

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
            
            Debug.Log(name + " Reached Target in test number " + testNumber);
            System.TimeSpan ts = System.DateTime.UtcNow - startTime;
            string time = (ts.TotalMilliseconds / 1000.0f).ToString();
            Debug.Log("Time needed to reach: " + time + "  ---  Total reward = " + totalReward);

            targetComponent.registerTime(time);

            //printLog();
            //foreach (Test agent in otherAgents)
            //    agent.printLog();

            ReachedTarget();
            return;
        }

        AddReward(-existenctialPenalty);

        CheckTargetProximity();

        moves++;

        if (moves >= maxMoves)
        {
            System.TimeSpan ts = System.DateTime.UtcNow - startTime;
            string timeInSeconds = (ts.TotalMilliseconds / 1000.0f).ToString();
            Debug.Log("Failed test number " + testNumber + " after " + timeInSeconds + " seconds" + "  ---  Total reward = " + totalReward);
            targetComponent.registerTime(timeInSeconds); //default value. if it doesn't reach the target, we set time to 0
            ReachedTarget();
            return;
        }

        if (CommunicationMode.Contains(Communication.FreeCommunication))
        {
            int messageIndex = actionBuffers.ContinuousActions.Length - 1;
            float message = actionBuffers.ContinuousActions[messageIndex];
            commList.Add(message.ToString());
            LastFreeComm = message;
        }
        // PrintLog();

    }

    private void PrintLog()
    {
        File.WriteAllLines("Communication_" + name + ".txt", commList);
    }

    private void CheckTargetProximity()
    {
        Vector3 dir = (Target.position - transform.position).normalized;
        if (Physics.Raycast(transform.position, dir, out RaycastHit hit))
            if (hit.collider.name.Equals(Target.name))
                AddReward((1 / hit.distance) * nearTargetReward);

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

    // If the agents are on sigth add the negative reward, otherwise nothing
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