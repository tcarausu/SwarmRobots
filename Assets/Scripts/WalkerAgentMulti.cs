using System.Collections.Generic;
using Unity.MLAgents;
using Unity.MLAgents.Actuators;
using Unity.MLAgents.Sensors;
using UnityEngine;
using Random = UnityEngine.Random;

public class WalkerAgentMulti : Agent
{
    public float playerSpeed = 10;
    public float existenctialPenalty = 0.001f;
    public float nearAgentPenalty = 0.1f; //Not implemented yet
    public float hitWallPenalty = 0.05f;
    public float hitAgentPenalty = 0.03f;

    public float checkpointReward = 0.15f;
    public float targetReward = 1;

    private Transform Swarm;
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
        {
            cp.SetActive(true);
        }

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
        //The only observation is the raycast 

        //TODO: add the position of close agents

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
        {
            transform.forward = direction;
        }

        // Rewards

        // Reached target
        if (reachedGoal)
        {
            WalkerAgentMulti[] agents = Swarm.GetComponentsInChildren<WalkerAgentMulti>();
            foreach(WalkerAgentMulti agent in agents)
            {
                agent.SetReward(targetReward);
                agent.EndEpisode();
            }

            MoveTarget();
        }
        else
            AddReward(-existenctialPenalty);
    }

    public override void Heuristic(in ActionBuffers actionsOut)
    {
        var continuousActionsOut = actionsOut.ContinuousActions;
        continuousActionsOut[0] = Input.GetAxis("Horizontal");
        continuousActionsOut[1] = Input.GetAxis("Vertical");
    }
}