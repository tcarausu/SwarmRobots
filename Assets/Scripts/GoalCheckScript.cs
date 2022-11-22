using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class GoalCheckScript : MonoBehaviour
{
    private void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag("agent"))
        {
            //other.gameObject.GetComponent<WalkerAgentMulti>().ReachGoal();
            if (other.TryGetComponent<WalkerAgentMulti>(out WalkerAgentMulti agentm))
            {
                agentm.ReachGoal();
            }
            else if (other.TryGetComponent<PocaWalkerAgent>(out PocaWalkerAgent agentp))
            {
                agentp.ReachGoal();
            }
        }
    }
}