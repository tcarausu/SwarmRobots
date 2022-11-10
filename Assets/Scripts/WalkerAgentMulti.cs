using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Unity.MLAgents;
using Unity.MLAgents.Sensors;
using Unity.MLAgents.Actuators;

public class WalkerAgentMulti : Agent
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

    public Transform SpawnArea;
    public Transform Target;
    public override void OnEpisodeBegin()
    {
        foreach(Checkpoint cp in clearedCheckpoints){
            cp.SetActive(true);
        }
        clearedCheckpoints.Clear();
        RndSpawn();
    }

    public void RndSpawn(){
        Vector3 spawnSize = SpawnArea.GetComponent<Renderer>().bounds.size;
        Vector3 rndPosition = new Vector3( Random.value * spawnSize.x - spawnSize.x/2, 1, Random.value * spawnSize.z - spawnSize.z/2);
        if(rndPosition.x > 0)
            rndPosition.x -= 1;
        else 
            rndPosition.x += 1;
        
        if(rndPosition.z > 0)
            rndPosition.z -= 1;
        else 
            rndPosition.z += 1;

        this.transform.localPosition = rndPosition;
        Debug.Log(rndPosition);
    }

    public void MoveTarget(){
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
        float distanceToTarget = Vector3.Distance(this.transform.position, Target.position);

        // Reached target
        if (distanceToTarget < 1.42f)
        {
            Transform parent = this.transform.parent;
            for(int i = 0; i < parent.childCount; i++)
            {
                GameObject Go = parent.GetChild(i).gameObject;
                if (Go.TryGetComponent<WalkerAgentMulti>(out WalkerAgentMulti agentm)){
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
