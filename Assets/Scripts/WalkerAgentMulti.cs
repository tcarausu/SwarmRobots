using System;
using System.Collections.Generic;
using Unity.MLAgents;
using Unity.MLAgents.Actuators;
using Unity.MLAgents.Sensors;
using UnityEngine;
using Random = UnityEngine.Random;

public class WalkerAgentMulti : Agent
{
    CharacterController controller;
    private List<Checkpoint> clearedCheckpoints;

    private Vector3 initialPosition;
    private Rigidbody rb;
    private  Vector3 spawnSize;

    void Start()
    {
        controller = GetComponent<CharacterController>();
        clearedCheckpoints = new List<Checkpoint>();

        initialPosition = transform.localPosition;
        rb = GetComponent<Rigidbody>();
         spawnSize = SpawnArea.GetComponent<Renderer>().bounds.size;

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

    public Transform SpawnArea;
    public Transform Target;

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
        //todo aless code
        // Vector3 rndPosition = new Vector3(Random.value * spawnSize.x - spawnSize.x / 2, 1,
        // Random.value * spawnSize.z - spawnSize.z / 2);

        var randomV = Random.value;
        Vector3 rndPosition = new Vector3(
            randomV * spawnSize.x - spawnSize.x / 2,
            initialPosition.y,
            randomV * spawnSize.z - spawnSize.z / 2);

        if (rndPosition.x > 0)
            rndPosition.x -= 1;
        else
            rndPosition.x += 1;

        if (rndPosition.z > 0)
            rndPosition.z -= 1;
        else
            rndPosition.z += 1;

        transform.localPosition = rndPosition;
        // Debug.Log(rndPosition);
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
            Transform parent = transform.parent;
            for (int i = 0; i < parent.childCount; i++)
            {
                GameObject Go = parent.GetChild(i).gameObject;
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

        //todo Aless code, instead of checking distance; checking if we got to the goal then restart the episode

        // float distanceToTarget = Vector3.Distance(transform.position, Target.position);
        //
        // // Reached target
        // if (distanceToTarget < 1.42f)
        // {
        //     print("reached goal"); // you can use print for some scripts, for others you need Debug.Log
        //     Transform parent = transform.parent;
        //     for (int i = 0; i < parent.childCount; i++)
        //     {
        //         GameObject Go = parent.GetChild(i).gameObject;
        //         if (Go.TryGetComponent<WalkerAgentMulti>(out WalkerAgentMulti agentm))
        //         {
        //             agentm.SetReward(1.0f);
        //             agentm.EndEpisode();
        //             rb.velocity = Vector3.zero;
        //         }
        //     }
        //     MoveTarget();
        // }
        // else
        // {
        //     AddReward(-0.0001f);
        // }
    }

    public override void Heuristic(in ActionBuffers actionsOut)
    {
        var continuousActionsOut = actionsOut.ContinuousActions;
        continuousActionsOut[0] = Input.GetAxis("Horizontal");
        continuousActionsOut[1] = Input.GetAxis("Vertical");
    }
}