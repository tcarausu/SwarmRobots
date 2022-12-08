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

struct AgentDistances
{
    public WalkerAgentMulti agent;
    public float distance;

    public AgentDistances(WalkerAgentMulti agent, float distance) : this()
    {
        this.agent = agent;
        this.distance = distance;
    }
    public void SetDistanceFrom(Vector3 point) { this.distance = Vector3.Distance(agent.transform.localPosition, point); }
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
        Position
    }

    public List<Communication> CommunicationMode;
    public Movement movementMode;
    public float playerSpeed = 10;
    public float rotationSensitivity = 10;

    private int numTargetsFound = 0;
    [Tooltip("This number represents the number of episodes that the target mantain his starting position")]
    public int firstChangeTargetPos = 10;

    [Header("Rewards")]
    private float existenctialPenalty = 0.001f;

    [Tooltip("The penalty is multiplied by 1/distance from the near agent if they are on sigth")]
    //private float nearAgentPenalty = 0.01f;
    private float nearAgentPenalty = 0.0f;

    private float hitWallPenalty = 0.01f;
    private float hitAgentPenalty = 0.003f;

    private float checkpointReward = 0.15f;
    private float targetReward = 1;
    private float nearTargetReward = 0.002f;

    // Communication
    private Dictionary<string, float> communicationMap;
    private readonly int CommunicationSpots = 3;
    private float LastFreeComm = 0;

    private Transform Swarm;
    private List<WalkerAgentMulti> otherAgents;
    private List<AgentDistances> otherAgentsDistance;
    private Transform Target;
    private SpawnAreas TargetSpawnAreas;

    private CharacterController controller;

    private List<Checkpoint> clearedCheckpoints;

    private Transform MySpawnArea;
    private SpawnCheck spawnCheck;
    private Vector3 initialPosition;
    private Vector3 spawnSize;
    private float length; // Since the agent is a cube edge length on the x is supposed to be length on y and z too

    [Header("The changing maze object in the same area as the agent")]
    public GameObject Mazes;
    [Tooltip("Set this to true if the area of the agent can change maze")]
    public bool hasRandomMaze;
    private Transform _activeMaze;
    private Transform Goal;



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

        var envParameters = Academy.Instance.EnvironmentParameters;
        existenctialPenalty = envParameters.GetWithDefault("existenctial", existenctialPenalty);
        nearAgentPenalty = envParameters.GetWithDefault("near_agent", nearAgentPenalty);

        hitWallPenalty = envParameters.GetWithDefault("hit_wall", hitWallPenalty);
        hitAgentPenalty = envParameters.GetWithDefault("hit_agent", hitAgentPenalty);

        checkpointReward = envParameters.GetWithDefault("checkpoint", checkpointReward);
        targetReward = envParameters.GetWithDefault("target", targetReward);
        nearTargetReward = envParameters.GetWithDefault("near_target", nearTargetReward);

        if (hasRandomMaze)
        {
            _activeMaze = Mazes.GetComponent<SelectRandomMaze>().getActiveMaze();
            Goal = _activeMaze.Find("GOAL");
        }
        else
            Goal = Mazes.transform.Find("GOAL");

        TargetSpawnAreas = Goal.Find("SpawnAreas").gameObject.GetComponent<SpawnAreas>();
        Target = Goal.Find("Target");

        otherAgents = new List<WalkerAgentMulti>(Swarm.GetComponentsInChildren<WalkerAgentMulti>());
        otherAgents.Remove(this);

        otherAgentsDistance = new List<AgentDistances>();
        foreach (var agent in otherAgents)
            otherAgentsDistance.Add(new AgentDistances(agent, 0));

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
            for (int i = 0; i < CommunicationSpots; i++)
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

    private bool reachedGoal;

    public void ReachGoal() {   reachedGoal = true;    }

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

        if (CommunicationMode.Contains(Communication.FreeCommunication))
        {
            int messageIndex = actionBuffers.ContinuousActions.Length - 1;
            float message = actionBuffers.ContinuousActions[messageIndex];
            LastFreeComm = message;
        }
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
            _activeMaze = Mazes.GetComponent<SelectRandomMaze>().getActiveMaze();
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