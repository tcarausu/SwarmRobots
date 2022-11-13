using System;
using System.Collections.Generic;
using Unity.MLAgents;
using Unity.MLAgents.Actuators;
using Unity.MLAgents.Sensors;
using UnityEngine;
using Random = UnityEngine.Random;

public class WalkerAgentMulti : Agent
{
    public Transform Swarm;
    public Transform Target;

    private Transform SpawnArea;
    private SpawnCheck spawnCheck;
    CharacterController controller;
    private List<Checkpoint> clearedCheckpoints;

    private Vector3 initialPosition;
    private Rigidbody rb;
    private Vector3 spawnSize;
    private float length; // Since the agent is a cube edge length on the x is supposed to be length on y and z too

    void Start()
    {
        controller = GetComponent<CharacterController>();
        clearedCheckpoints = new List<Checkpoint>();

        spawnCheck = Swarm.gameObject.GetComponent<SpawnCheck>();
        SpawnArea = Swarm.Find("SpawnArea");
        initialPosition = transform.localPosition;
        rb = GetComponent<Rigidbody>();
        spawnSize = SpawnArea.GetComponent<Renderer>().bounds.size;
        length = GetComponent<BoxCollider>().size.x;
        spawnSize.x = spawnSize.x - length/2;
        spawnSize.z = spawnSize.z - length/2;
    }

    public void checkpoint(Checkpoint cp)
    {
        AddReward(0.2f);
        clearedCheckpoints.Add(cp);
    }

    // void OnCollisionEnter(Collision collision)
    // {
    //     if(collision.gameObject.name != "WalkerAgent")
    //     {
    //     //    Debug.Log("Collided with " + collision.gameObject.name);
    //         AddReward(-0.01f);
    //     }
    // }


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
        while (!spawnCheck.isSafePosition(rndPosition, length));
        
        transform.localPosition = rndPosition;
        
    }

    private void MoveTarget()
    {
        // Move the target to a new spot
        Target.localPosition = new Vector3(Random.value * 34 - 17, Target.localPosition.y, Target.localPosition.z);
        reachedGoal = false;
    }

    public override void CollectObservations(VectorSensor sensor)
    {
        // Target and Agent positions
        sensor.AddObservation(Target.localPosition.x);
        sensor.AddObservation(Target.localPosition.z);
        sensor.AddObservation(transform.localPosition.x);
        sensor.AddObservation(transform.localPosition.z);
        // Agent direction (useful to understand ray perception)
        //sensor.AddObservation(this.transform.rotation.eulerAngles.y);
    }

    public float playerSpeed = 10;
    public bool reachedGoal;

    public override void OnActionReceived(ActionBuffers actionBuffers)
    {
        // Actions, size = 2
        Vector3 direction = Vector3.zero;
        direction.x = actionBuffers.ContinuousActions[0];
        direction.z = actionBuffers.ContinuousActions[1];

        controller.Move(direction * Time.deltaTime * playerSpeed);
        if (direction != Vector3.zero)
        {
            transform.forward = direction;
        }

        // Rewards

        // Reached target
        if (reachedGoal)
        {
            
            for (int i = 0; i < Swarm.childCount; i++)
            {
                GameObject Go = Swarm.GetChild(i).gameObject;
                if (Go.TryGetComponent(out WalkerAgentMulti agentm))
                {
                    agentm.SetReward(1.0f);
                    agentm.EndEpisode();
                }
            }

            MoveTarget();
        }
        else
        {
            AddReward(-0.0001f);
        }

    }

    public override void Heuristic(in ActionBuffers actionsOut)
    {
        var continuousActionsOut = actionsOut.ContinuousActions;
        continuousActionsOut[0] = Input.GetAxis("Horizontal");
        continuousActionsOut[1] = Input.GetAxis("Vertical");
    }
}