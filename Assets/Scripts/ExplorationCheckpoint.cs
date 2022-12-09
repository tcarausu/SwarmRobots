using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ExplorationCheckpoint : MonoBehaviour
{

    private ExplorationCheckpointsController controller;


    void Start()
    {
            controller = gameObject.GetComponentInParent(typeof(ExplorationCheckpointsController)) as ExplorationCheckpointsController;
    }

    private void OnTriggerEnter(Collider other)
    {
        if (other.TryGetComponent<WalkerAgentSingle>(out WalkerAgentSingle agents))
        {
            controller.increase();
            this.gameObject.SetActive(false);
        }
        else if (other.TryGetComponent<WalkerAgentMulti>(out WalkerAgentMulti agentm))
        {
            controller.increase();
            this.gameObject.SetActive(false);

        }
        else if (other.TryGetComponent<PocaWalkerAgent>(out PocaWalkerAgent agentp))
        {
            controller.increase();
            this.gameObject.SetActive(false);
        }
        else if (other.TryGetComponent<Test>(out Test agentt))
        {
            controller.increase();
            this.gameObject.SetActive(false);
        }


    }

    public void SetActive(bool active)
    {
        this.gameObject.SetActive(active);
    }
}
