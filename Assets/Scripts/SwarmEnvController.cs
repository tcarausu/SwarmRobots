using System.Collections.Generic;
using Unity.MLAgents;
using Unity.MLAgents.Actuators;
using Unity.MLAgents.Policies;
using Unity.MLAgents.Sensors;
using UnityEngine;
using Random = UnityEngine.Random;

public class SwarmEnvController : MonoBehaviour
{
    private List<PocaWalkerAgent> agents;
    private SimpleMultiAgentGroup m_AgentGroup;
    private Transform Swarm;

    void Start()
    {
        Swarm = gameObject.transform.Find("Swarm");
        agents = new List<PocaWalkerAgent>(Swarm.GetComponentsInChildren<PocaWalkerAgent>());

        // Initialize TeamManager
        m_AgentGroup = new SimpleMultiAgentGroup();

        //Add agents
        foreach (var agent in agents)
        {
            m_AgentGroup.RegisterAgent(agent);
        }
    }

    public void targetFound()
    {
        Debug.Log("target found");
        m_AgentGroup.AddGroupReward(1f);
        m_AgentGroup.EndGroupEpisode();
    }

}
