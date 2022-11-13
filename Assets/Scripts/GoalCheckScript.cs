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
            print("goal yes yes");
            other.gameObject.GetComponent<WalkerAgentMulti>().reachedGoal = true;
        }
    }
}