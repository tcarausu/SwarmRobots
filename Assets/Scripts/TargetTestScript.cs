using System.Collections.Generic;
using UnityEngine;
using System.IO;


public class TargetTestScript : MonoBehaviour
{
    public List<Vector3> TargetPositions;
    public string trainingAreaName = "";

    private List<string> TimeToTarget;
    private readonly string path = "OurModels/ReportData/TimeToTarget/";                   
    private int count;

    private ExplorationCheckpointsController expCheckController;

    void Start()
    {
        TimeToTarget = new List<string>();
        count = 0;
        transform.localPosition = TargetPositions[count];
        count += 1;

        Transform tExploCheckpoints = transform.parent.parent.Find("ExplorationCheckpoints");
        expCheckController = tExploCheckpoints.gameObject.GetComponent<ExplorationCheckpointsController>();
    }

    public Vector3 getTargetPosition()
    {
        Vector3 newPos = TargetPositions[count % TargetPositions.Count];
        count += 1;
        return newPos;
    }

    public int getTotalPositions()
    {
        return TargetPositions.Count;
    }

    
    public void registerTime(string time)
    {
        TimeToTarget.Add(time);
        expCheckController.restart(true);
    }

    public void saveTimeToTarget(string modelName)
    {
#if UNITY_EDITOR
			File.WriteAllLines(path + modelName + "/" + trainingAreaName + ".dat", TimeToTarget);
            expCheckController.saveExplorationRate(modelName, trainingAreaName);
#endif
        TimeToTarget.Clear();
        count = 0;
    }

    public void initDirectory(string modelName)
    {
        Directory.CreateDirectory(path + modelName);
    }

}
