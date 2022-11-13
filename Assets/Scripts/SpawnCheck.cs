using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class SpawnCheck : MonoBehaviour
{
    private List<Transform> Agents;
    // Start is called before the first frame update
    void Start()
    {
        Agents = new List<Transform>();
        for (int i = 0; i < transform.childCount; i++)
        {
            Transform t = transform.GetChild(i);
            GameObject Go = t.gameObject;
            if (Go.GetComponent<WalkerAgentMulti>() != null)
            {
                Agents.Add(t);
            }
        }
    }

    // Returns true if pos can be used as a spawn position for a new agent with edge size length
    public bool isSafePosition(Vector3 pos, float length){
        foreach(var agent in Agents)
        {
            Vector3 agentPos = agent.localPosition;
            if (Mathf.Abs(agentPos.x - pos.x) < length && 
                Mathf.Abs(agentPos.z - pos.z) < length)
            {
                return false;
            }
        }
        return true;
    }

}
