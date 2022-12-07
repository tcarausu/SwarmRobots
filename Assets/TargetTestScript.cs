using System.Collections.Generic;
using UnityEngine;
using System.Linq;
using System.ComponentModel;
using System.IO;


public class TargetTestScript : MonoBehaviour
{
    public List<Vector3> TargetPositions;
    public string trainingAreaName = "";

    private List<string> TimeToTarget;
    private string path = "OurModels/";                   
    private int count;

    void Start()
    {
        TimeToTarget = new List<string>();
        count = 0;
        transform.localPosition = TargetPositions[count];
        count += 1;
    }

    public Vector3 getTargetPosition()
    {
        Vector3 newPos = TargetPositions[count];
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
    }

    public void saveTimeToTarget(string modelName)
    {
        File.WriteAllLines(path + modelName + "/" + trainingAreaName + ".dat", TimeToTarget);
    }


    public void initDirectory(string modelName)
    {
        Directory.CreateDirectory(path + modelName);
    }

}
