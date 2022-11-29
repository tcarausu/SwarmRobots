using System.Collections.Generic;
using Unity.MLAgents;
using Unity.MLAgents.Actuators;
using Unity.MLAgents.Policies;
using Unity.MLAgents.Sensors;
using UnityEngine;
using Random = UnityEngine.Random;

public class Test : Agent
{
    public enum Movement { UpAndRight, ForwardAndRotate }
    public Movement mode;
    public float playerSpeed = 20;
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

    public bool useCommunication;
    private List<float> communicationList;

    private Transform Swarm;
    private List<Test> otherAgents;
    private Transform Target;
//    private SpawnAreas TargetSpawnAreas;

    private CharacterController controller;

//    private List<Checkpoint> clearedCheckpoints;

//    private Transform MySpawnArea;
//    private SpawnCheck spawnCheck;
    private Vector3 initialPosition;
//    private Vector3 spawnSize;
//    private float length; // Since the agent is a cube edge length on the x is supposed to be length on y and z too

    private int testNumber = 0;
    private System.DateTime startTime;
    public List<Vector3> TargetPositions; 
    public int maxMoves;
    private int moves = 0;

    void Start()
    {
        controller = GetComponent<CharacterController>();
 //       clearedCheckpoints = new List<Checkpoint>();

        Swarm = transform.parent;
 //       spawnCheck = Swarm.gameObject.GetComponent<SpawnCheck>();
 //       MySpawnArea = Swarm.Find("SpawnArea");
        initialPosition = transform.localPosition;
 //       spawnSize = MySpawnArea.GetComponent<Renderer>().bounds.size;
 //       length = GetComponent<BoxCollider>().size.x;
 //       spawnSize.x -= length / 2;
 //       spawnSize.z -= length / 2;

        Transform Goal = Swarm.parent.Find("GOAL");
 //       GameObject go = Goal.Find("SpawnAreas").gameObject;
 //       TargetSpawnAreas = go.GetComponent<SpawnAreas>();
        Target = Goal.Find("Target");

        otherAgents = new List<Test>(Swarm.GetComponentsInChildren<Test>());
        otherAgents.Remove(this);

        // Compute observation size based on the useCommunication parameter
        int obsSize = 0;
        if (useCommunication)
        {
            obsSize = otherAgents.Count;
            communicationList = new List<float>(new float[(int)(obsSize)]);
        }

        // Since I can't set the size from here I just notify the user
        Debug.Assert(GetComponent<BehaviorParameters>().BrainParameters.VectorObservationSize == obsSize,
            "Wrong observation size, change it from the prefab of the Agent. Actual value = " +
            GetComponent<BehaviorParameters>().BrainParameters.VectorObservationSize + " but expected " + obsSize +
            "\nRemember you have Communication set to " + useCommunication);

        startTime = System.DateTime.UtcNow;
        moves = 0;
    }

    public void Checkpoint(Checkpoint cp)
    {
        AddReward(checkpointReward);
 //       clearedCheckpoints.Add(cp);
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
        //foreach (Checkpoint cp in clearedCheckpoints)
        //    cp.SetActive(true);

        //clearedCheckpoints.Clear();
        ResetPosition();
        testNumber++;

        if (testNumber-1 == TargetPositions.Count)
        {
            Application.Quit();
            UnityEditor.EditorApplication.isPlaying = false;
        }
        
        startTime = System.DateTime.UtcNow;
        moves = 0;
    }

    private void ResetPosition()
    {
        transform.localPosition = initialPosition;
    }

    //private void RndSpawn()
    //{
    //    Vector3 rndPosition;
    //    do
    //    {
    //        rndPosition = new Vector3(
    //        Random.value * spawnSize.x - spawnSize.x / 2,
    //        initialPosition.y,
    //        Random.value * spawnSize.z - spawnSize.z / 2);
    //    }
    //    while (!spawnCheck.IsSafePosition(rndPosition, length));

    //    transform.localPosition = rndPosition;

    //}

    private void MoveTarget()
    {
        // Move the target to a new spot
        if(testNumber - 1 < TargetPositions.Count)
            Target.localPosition = TargetPositions[testNumber-1];
        reachedGoal = false;
    }

    public override void CollectObservations(VectorSensor sensor)
    {

        //The only observation is the raycast if communication is not used
        if (useCommunication)
        {
            CheckNearAgentsAndUpdateCommunication();
            sensor.AddObservation(communicationList);
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
    public void ReachGoal() { reachedGoal = true; }

    public override void OnActionReceived(ActionBuffers actionBuffers)
    {
        if (mode.Equals(Movement.UpAndRight))
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
            Debug.Log("Reached Target in test number " + testNumber);
            System.TimeSpan ts = System.DateTime.UtcNow - startTime;
            Debug.Log("Time needed to reach: " + (ts.TotalMilliseconds/1000.0f).ToString());
            ReachedTarget();
            return;
        }

        moves++;
        if(moves >= maxMoves)
        {
            System.TimeSpan ts = System.DateTime.UtcNow - startTime;
            Debug.Log("Failed test number " + testNumber + " after " + (ts.TotalMilliseconds / 1000.0f).ToString() + " seconds");
            ReachedTarget();
            return;
        }
        
        AddReward(-existenctialPenalty);
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
    }

    public override void Heuristic(in ActionBuffers actionsOut)
    {
        var continuousActionsOut = actionsOut.ContinuousActions;
        continuousActionsOut[0] = Input.GetAxis("Horizontal");
        continuousActionsOut[1] = Input.GetAxis("Vertical");
    }
}