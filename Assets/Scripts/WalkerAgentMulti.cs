using System.Collections.Generic;
using Unity.MLAgents;
using Unity.MLAgents.Actuators;
using Unity.MLAgents.Policies;
using Unity.MLAgents.Sensors;
using UnityEngine;
using Random = UnityEngine.Random;

public class WalkerAgentMulti : Agent
{
    public float playerSpeed = 10;

    public float existenctialPenalty = 0.001f;
    [Tooltip("The penalty is multiplied by 1/distance from the near agent if they are on sigth")]
    [Header("Inversely proportional to distance")]
    public float nearAgentPenalty = 0.1f;
    public float hitWallPenalty = 0.05f;
    public float hitAgentPenalty = 0.03f;

    public float checkpointReward = 0.15f;
    public float targetReward = 1;

    private bool useCommunication; // Retreived from the training area, remember to set the observation size correctly in the prefab
    private List<float> communicationList;

    private Transform Swarm;
    private List<WalkerAgentMulti> otherAgents;
    private Transform Target;
    private SpawnAreas TargetSpawnAreas;

    private CharacterController controller;

    private List<Checkpoint> clearedCheckpoints;

    private Transform MySpawnArea;
    private SpawnCheck spawnCheck;
    private Vector3 initialPosition;
    private Vector3 spawnSize;
    private float length; // Since the agent is a cube edge length on the x is supposed to be length on y and z too

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
        spawnSize.x -= length/2;
        spawnSize.z -= length/2;

        Transform Goal = Swarm.parent.Find("GOAL");
        GameObject go = Goal.Find("SpawnAreas").gameObject;
        TargetSpawnAreas = go.GetComponent<SpawnAreas>();
        Target = Goal.Find("Target");

        useCommunication = Swarm.parent.GetComponent<CommonParameters>().useCommunication;

        otherAgents = new List<WalkerAgentMulti>(Swarm.GetComponentsInChildren<WalkerAgentMulti>());
        otherAgents.Remove(this);

        // Compute observation size based on the useCommunication parameter
        int obsSize = 0;
        if (useCommunication)
        {
            obsSize = otherAgents.Count;
            communicationList = new List<float>(obsSize);
        }

        // Since I can't set the size from here I just notify the user
        Debug.Assert(GetComponent<BehaviorParameters>().BrainParameters.VectorObservationSize == obsSize,
            "Wrong observation size, change it from the prefab of the Agent. Actual value = " +
            GetComponent<BehaviorParameters>().BrainParameters.VectorObservationSize + " but expected " + obsSize +
            "\nRemember you have Communication set to " + useCommunication);
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
        } 
        while (!spawnCheck.IsSafePosition(rndPosition, length));
        
        transform.localPosition = rndPosition;
        
    }

    private void MoveTarget()
    {
        // Move the target to a new spot
        Target.localPosition = TargetSpawnAreas.GetRndPosition();
        reachedGoal = false;
    }

    public override void CollectObservations(VectorSensor sensor)
    {
        //The only observation is the raycast if communication is used
        if (useCommunication)
            sensor.AddObservation(communicationList);

        // Target and Agent positions
        //sensor.AddObservation(Target.localPosition.x);
        //sensor.AddObservation(Target.localPosition.z);
        //sensor.AddObservation(transform.localPosition.x);
        //sensor.AddObservation(transform.localPosition.z);
        // Agent direction (useful to understand ray perception)
        //sensor.AddObservation(this.transform.rotation.eulerAngles.y);
    }

    private bool reachedGoal;
    public void ReachGoal() { reachedGoal = true;}

    public override void OnActionReceived(ActionBuffers actionBuffers)
    {
        // Actions, size = 2
        Vector3 direction = Vector3.zero;
        direction.x = actionBuffers.ContinuousActions[0];
        direction.z = actionBuffers.ContinuousActions[1];

        controller.Move(playerSpeed * Time.deltaTime * direction);
        if (direction != Vector3.zero)
            transform.forward = direction;
        

        if (reachedGoal)
            ReachedTarget();
        else
            AddReward(-existenctialPenalty);

        // Near agent penalty
        CheckNearAgents();
    }

    // Set the reward of all agents to 1, End the episode and move the target
    private void ReachedTarget()
    {
        SetReward(targetReward);
        EndEpisode();
        foreach (WalkerAgentMulti agent in otherAgents)
        {
            agent.SetReward(targetReward);
            agent.EndEpisode();
        }

        MoveTarget();
    }

    // If the agents are on sigth add the negative reward, otherwise 0,
    // If useCommunication is set to true build the communication list
    private void CheckNearAgents()
    {
        Vector3 dir;
        if (useCommunication)
            communicationList.Clear();
        foreach (Agent agent in otherAgents)
        {
            dir = (agent.transform.position - transform.position).normalized;
            if (Physics.Raycast(transform.position, dir, out RaycastHit hit))
            {
                if (hit.collider.name.Equals(agent.name))
                {
                    AddReward(-(1 / hit.distance) * nearAgentPenalty);
                    if (useCommunication)
                        communicationList.Add(hit.distance);
                }
                else if (useCommunication)
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