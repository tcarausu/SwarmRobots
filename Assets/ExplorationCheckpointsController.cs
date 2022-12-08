using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.IO;
using System.Linq;

public class ExplorationCheckpointsController : MonoBehaviour
{

    private int counter = 0;
    private int total;
    private Component[] myCheckpoints;
    private string path = "OurModels/ExplorationRate/";

    private List<string> rates;

    // Start is called before the first frame update
    void Start()
    {
        rates = new List<string>();
        myCheckpoints = gameObject.GetComponentsInChildren<ExplorationCheckpoint>(true);
    }

    public void increase()
    {
        counter += 1;
    }

    public void restart(bool hasToAddRate)
    {
        if(hasToAddRate) 
            addRate();
        counter = 0;
        foreach (ExplorationCheckpoint c in myCheckpoints)
        {
            c.SetActive(true);
        }
    }

    public void saveExplorationRate(string modelName,string trainingAreaName)
    {
        restart(false);
        File.WriteAllLines(path + modelName + "/" + trainingAreaName + ".dat", rates);
        rates.Clear();

    }

    public void initDirectory(string modelName)
    {
        Directory.CreateDirectory(path + modelName);
    }

    public void addRate()
    {
        rates.Add(((float)counter / myCheckpoints.Count()).ToString());
    }






}
