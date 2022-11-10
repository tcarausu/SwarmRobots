using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Checkpoint : MonoBehaviour
{

    private void OnTriggerEnter(Collider other){
        if(other.TryGetComponent<WalkerAgent>(out WalkerAgent agent)){
            agent.checkpoint(this);
            this.gameObject.SetActive(false);
        }
    }

    public void SetActive(bool active){
        this.gameObject.SetActive(active);
    }
}
