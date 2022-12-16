using UnityEngine;
using System.Security.Cryptography.X509Certificates;
using System.Collections.Generic;
using System.Threading;

public class GoalCheckScript : MonoBehaviour
{

    private void OnTriggerEnter(Collider other)
    {
        if (other.TryGetComponent<WalkerAgentMulti>(out WalkerAgentMulti agentm))
        {
            agentm.ReachGoal();
        }
        else if (other.TryGetComponent<Test>(out Test agentt))
        {
            agentt.ReachGoal();
        }
    }
}