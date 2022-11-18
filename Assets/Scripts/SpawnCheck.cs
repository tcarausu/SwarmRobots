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

    // private readonly float sqrt2 = Mathf.Sqrt(3);
    // Returns true if pos can be used as a spawn position for a new agent with edge size length
    public bool IsSafePosition(Vector3 pos, float length){
        //float maxDistance = length * sqrt2; // Conidering diagonal of the cube
        foreach (var agent in Agents)
        {
           
            Vector3 agentPos = agent.localPosition;
            //Debug.Log(transform.parent.name + " --> " + agent.name);
            //Debug.Log(agentPos + " , " + pos);
            //Debug.Log(Vector3.Distance(agentPos, pos));
            if (Mathf.Abs(agentPos.x - pos.x) < length ||
                Mathf.Abs(agentPos.z - pos.z) < length)
                return false;

        }
        return true;
    }

}
