    using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Unity.MLAgents;
using Unity.MLAgents.Sensors;
using Unity.MLAgents.Actuators;

public class WalkerAgentSingle : Agent
{
    CharacterController controller;
    private List<Checkpoint> clearedCheckpoints;

    void Start () 
    {
        controller = GetComponent<CharacterController>();
        clearedCheckpoints = new List<Checkpoint>();
    }

    public void checkpoint(Checkpoint cp){
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

    public Transform Target;
    public override void OnEpisodeBegin()
    {
        foreach(Checkpoint cp in clearedCheckpoints){
            cp.SetActive(true);
        }
        clearedCheckpoints.Clear();

        this.transform.localPosition = new Vector3( 15.0f, this.transform.localPosition.y, 42.0f);
        
        // Move the target to a new spot
        Target.localPosition = new Vector3(Random.value * 34 - 17, Target.localPosition.y, Target.localPosition.z) ;
    }

    public override void CollectObservations(VectorSensor sensor)
    {
        // Target and Agent positions
        sensor.AddObservation(Target.localPosition.x);
        sensor.AddObservation(Target.localPosition.z);
        sensor.AddObservation(this.transform.localPosition.x);
        sensor.AddObservation(this.transform.localPosition.z);
        // Agent direction (useful to understand ray perception)
        //sensor.AddObservation(this.transform.rotation.eulerAngles.y);
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
