using UnityEngine;

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