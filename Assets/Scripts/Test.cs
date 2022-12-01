using System.Collections.Generic;
using System.Collections.Specialized;
using System.Diagnostics;
using System.Security.Cryptography;
using Unity.MLAgents;
using Unity.MLAgents.Actuators;
using Unity.MLAgents.Policies;
using Unity.MLAgents.Sensors;
using UnityEngine;

using Debug = UnityEngine.Debug;

public class Test : Agent
{
    public enum Movement
    {
        UpAndRight,
        ForwardAndRotate,
        DiscreteActions
    }

    private Rigidbody m_AgentRb;

    public Movement mode;
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

    private int numEpisodes = 0;
    public int changePosTarget = 10;


    // Retrieved from the training area, remember to set the observation size correctly in the prefab
    public bool useCommunication;

    private List<float> communicationList;

    private Transform Swarm;
    private List<Test> otherAgents;
    private Transform Target;
    private SpawnAreas TargetSpawnAreas;

    private CharacterController controller;

    private List<Checkpoint> clearedCheckpoints;

    private Vector3 targetInitialPosition;

    private Transform MySpawnArea;
    private SpawnCheck spawnCheck;
    private Vector3 initialPosition;
    private Vector3 spawnSize;
    private float length; // Since the agent is a cube edge length on the x is supposed to be length on y and z too

    public GameObject usableTrainingArea;
    private Transform _activeMaze;
    private Transform Goal;

    public bool hasRandomMaze;

    [System.NonSerialized]
    public bool seenTarget = false;

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

        m_AgentRb = GetComponent<Rigidbody>();

        if (hasRandomMaze)
            activateTheMaze();
        else
            useExisitingMaze();
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


    private void useExisitingMaze()
    {
        Goal = usableTrainingArea.transform.Find("GOAL");
        // Transform Goal = Swarm.parent.Find("GOAL");
        TargetSpawnAreas = Goal.Find("SpawnAreas").gameObject.GetComponent<SpawnAreas>();
        Target = Goal.Find("Target");

        targetInitialPosition = Target.localPosition;

        otherAgents = new List<Test>(Swarm.GetComponentsInChildren<Test>());
        otherAgents.Remove(this);

        // Compute observation size based on the useCommunication parameter
        int obsSize = 0;
        if (useCommunication)
        {
            obsSize = otherAgents.Count + 4;
            communicationList = new List<float>(new float[obsSize]);
        }

        // Since I can't set the size from here I just notify the user
        Debug.Assert(GetComponent<BehaviorParameters>().BrainParameters.VectorObservationSize == obsSize,
            "Wrong observation size, change it from the prefab of the Agent. Actual value = " +
            GetComponent<BehaviorParameters>().BrainParameters.VectorObservationSize + " but expected " + obsSize +
            "\nRemember you have Communication set to " + useCommunication);
    }

    private void activateTheMaze()
    {
        //getting the objectList of Mazes
        _activeMaze = usableTrainingArea.GetComponent<SelectRandomMaze>().getActiveMaze();

        Goal = _activeMaze.Find("GOAL");
        // Transform Goal = Swarm.parent.Find("GOAL");
        TargetSpawnAreas = Goal.Find("SpawnAreas").gameObject.GetComponent<SpawnAreas>();
        Target = Goal.Find("Target");

        otherAgents = new List<Test>(Swarm.GetComponentsInChildren<Test>());
        otherAgents.Remove(this);

        // Compute observation size based on the useCommunication parameter
        int obsSize = 0;
        if (useCommunication)
        {
            obsSize = otherAgents.Count + 2;
            communicationList = new List<float>(new float[obsSize]);
        }

        // Since I can't set the size from here I just notify the user
        Debug.Assert(GetComponent<BehaviorParameters>().BrainParameters.VectorObservationSize == obsSize,
            "Wrong observation size, change it from the prefab of the Agent. Actual value = " +
            GetComponent<BehaviorParameters>().BrainParameters.VectorObservationSize + " but expected " + obsSize +
            "\nRemember you have Communication set to " + useCommunication);
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

        if (numEpisodes % changePosTarget == 0)
        {
            Debug.Log("target moved");
            Target.localPosition = TargetSpawnAreas.GetRndPosition();
            targetInitialPosition = Target.localPosition;

        }
        else
        {
            Target.localPosition = targetInitialPosition;
        }

        reachedGoal = false;
    }

    public override void CollectObservations(VectorSensor sensor)
    {
        //The only observation is the raycast if communication is not used
        if (useCommunication)
        {
            CheckNearAgentsAndUpdateCommunication();
            sensor.AddObservation(communicationList);
            sensor.AddObservation(transform.localPosition.x);
            sensor.AddObservation(transform.localPosition.z);
        }
        else
            CheckNearAgents();


        // Target and Agent positions
        //sensor.AddObservation(Target.localPosition.x);
        //sensor.AddObservation(Target.localPosition.z);
        //sensor.AddObservation(transform.localPosition.x);
        //sensor.AddObservation(transform.localPosition.z);
        // Agent direction (useful to understand ray perception)
        //sensor.AddObservation(this.transform.rotation.eulerAngles.y);
    }

    private bool reachedGoal;

    public void ReachGoal()
    {
        reachedGoal = true;
    }

    public override void OnActionReceived(ActionBuffers actionBuffers)
    {
        if (mode.Equals(Movement.DiscreteActions))
        {

            var dirToGo = Vector3.zero;
            var rotateDir = Vector3.zero;

            var action = actionBuffers.DiscreteActions[0];
            Debug.Log(action);
            Debug.Log(transform.forward);

            switch (action)
            {
                case 1:
                    dirToGo = transform.forward * 1f;
                    break;
                case 2:
                    dirToGo = transform.forward * -1f;
                    break;
                case 3:
                    rotateDir = transform.up * 1f;
                    break;
                case 4:
                    rotateDir = transform.up * -1f;
                    break;
                case 5:
                    dirToGo = transform.right * -0.75f;
                    break;
                case 6:
                    dirToGo = transform.right * 0.75f;
                    break;
            }
            transform.Rotate(rotateDir * rotationSensitivity);
            controller.Move(dirToGo * Time.deltaTime * playerSpeed);
        }
        else if (mode.Equals(Movement.UpAndRight))
        {
            Vector3 direction = Vector3.zero;
            direction.x = actionBuffers.ContinuousActions[0];
            direction.z = actionBuffers.ContinuousActions[1];

            controller.Move(playerSpeed * Time.deltaTime * direction);
            if (direction != Vector3.zero)
                transform.forward = direction;
        }
        else if (mode.Equals(Movement.ForwardAndRotate))
        {
            var rotation = actionBuffers.ContinuousActions[0];
            var forwardMovement = actionBuffers.ContinuousActions[1];

            controller.Move(forwardMovement * playerSpeed * Time.deltaTime * transform.forward);
            transform.Rotate(rotation * rotationSensitivity * Vector3.up);
        }



        if (reachedGoal)
        {
            ReachedTarget();
            return;
        }


    }

    // Set the reward of all agents to 1, End the episode and move the target
    private void ReachedTarget()
    {
        SetReward(targetReward);
        EndEpisode();
        numEpisodes += 1;

        foreach (Test agent in otherAgents)
        {
            agent.numEpisodes += 1;
            agent.SetReward(targetReward);
            agent.EndEpisode();
        }

        if (hasRandomMaze)
            activateTheMaze();
        else
            useExisitingMaze();

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
        AddReward(-existenctialPenalty);

        Vector3 dir;
        communicationList.Clear();

        foreach (Agent agent in otherAgents)
        {
            dir = (agent.transform.position - transform.position).normalized;
            if (Physics.Raycast(transform.position, dir, out RaycastHit hit))
            {
                if (hit.collider.name.Equals(agent.name))
                {
                    AddReward(-(1 / hit.distance) * nearAgentPenalty);
                    communicationList.Add(hit.distance);
                }
                else
                    communicationList.Add(0);
            }
        }


        Vector3 dirT = (Target.position - transform.position).normalized;
        if (Physics.Raycast(transform.position, dirT, out RaycastHit hitT))
        {
            if (hitT.collider.name.Equals(Target.name))
            {
                AddReward((1 / hitT.distance) * nearTargetReward);
                communicationList.Add(Target.localPosition.x);
                communicationList.Add(Target.localPosition.z);
                if (!seenTarget) //first time it is seen
                {
                    seenTarget = true;
                    foreach (Test agent in otherAgents)
                    {
                        agent.seenTarget = true;
                    }
                }
            }
            else
            {
                if (seenTarget)
                {
                    communicationList.Add(Target.localPosition.x);
                    communicationList.Add(Target.localPosition.z);
                }
                else
                {
                    communicationList.Add(0);
                    communicationList.Add(0);
                }

            }

        }



    }

    public override void Heuristic(in ActionBuffers actionsOut)
    {
        if (mode.Equals(Movement.DiscreteActions))
        {
            var discreteActionsOut = actionsOut.DiscreteActions;
            if (Input.GetKey(KeyCode.D))
            {
                discreteActionsOut[0] = 3;
            }
            else if (Input.GetKey(KeyCode.W))
            {
                discreteActionsOut[0] = 1;
            }
            else if (Input.GetKey(KeyCode.A))
            {
                discreteActionsOut[0] = 4;
            }
            else if (Input.GetKey(KeyCode.S))
            {
                discreteActionsOut[0] = 2;
            }
        }

        else
        {

            var continuousActionsOut = actionsOut.ContinuousActions;
            continuousActionsOut[0] = Input.GetAxis("Horizontal");
            continuousActionsOut[1] = Input.GetAxis("Vertical");
        }
    }
}