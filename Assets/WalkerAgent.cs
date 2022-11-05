using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Unity.MLAgents;
using Unity.MLAgents.Sensors;
using Unity.MLAgents.Actuators;

public class WalkerAgent : Agent
{
    CharacterController controller;
    void Start () 
    {
        controller = GetComponent<CharacterController>();
    }

    // void OnCollisionEnter(Collision collision)
    // {
    //     if(collision.gameObject.name != "WalkerAgent")
    //     {
    //     //    Debug.Log("Collided with " + collision.gameObject.name);
    //         AddReward(-0.01f);
    //     }
    // }

    public Transform Target;
    public override void OnEpisodeBegin()
    {
        this.transform.localPosition = new Vector3( 15.0f, 2.0f, 42.0f);

        // Move the target to a new spot
        Target.localPosition = new Vector3(Random.value * 34 - 17, Target.localPosition.y,Target.localPosition.z) ;
    }

    public override void CollectObservations(VectorSensor sensor)
    {
        // Target and Agent positions
        sensor.AddObservation(Target.localPosition);
        sensor.AddObservation(this.transform.localPosition);
    }

    public float playerSpeed = 10;
    public override void OnActionReceived(ActionBuffers actionBuffers)
    {
        // Actions, size = 2
        Vector3 direction = Vector3.zero;
        direction.x = actionBuffers.ContinuousActions[0];
        direction.z = actionBuffers.ContinuousActions[1];
        controller.Move(direction * Time.deltaTime * playerSpeed);
        if (direction != Vector3.zero)
        {
            this.transform.forward = direction;
        }

        // Rewards
        float distanceToTarget = Vector3.Distance(this.transform.localPosition, Target.localPosition);

        // Reached target
        if (distanceToTarget < 1.42f)
        {
            SetReward(1.0f);
            EndEpisode();
        }
        else
        {
            SetReward(-0.0001f);
        }

    }

    public override void Heuristic(in ActionBuffers actionsOut)
    {
        var continuousActionsOut = actionsOut.ContinuousActions;
        continuousActionsOut[0] = Input.GetAxis("Horizontal");
        continuousActionsOut[1] = Input.GetAxis("Vertical");
    }
}
