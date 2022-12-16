using UnityEngine;

public class Checkpoint : MonoBehaviour
{

    private void OnTriggerEnter(Collider other){
        if (other.TryGetComponent<WalkerAgentMulti>(out WalkerAgentMulti agentm)){
            agentm.Checkpoint(this);
            this.gameObject.SetActive(false);
        }
    }

    public void SetActive(bool active){
        this.gameObject.SetActive(active);
    }
}
