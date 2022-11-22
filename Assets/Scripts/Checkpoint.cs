using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Checkpoint : MonoBehaviour
{

    private void OnTriggerEnter(Collider other){
        if(other.TryGetComponent<WalkerAgentSingle>(out WalkerAgentSingle agents)){
            agents.checkpoint(this);
            this.gameObject.SetActive(false);
        }
        else if (other.TryGetComponent<WalkerAgentMulti>(out WalkerAgentMulti agentm)){
            agentm.Checkpoint(this);
            this.gameObject.SetActive(false);
        }
        else if (other.TryGetComponent<PocaWalkerAgent>(out PocaWalkerAgent agentp))
        {
            agentp.Checkpoint(this);
            this.gameObject.SetActive(false);
        }
    }

    public void SetActive(bool active){
        this.gameObject.SetActive(active);
    }
}
