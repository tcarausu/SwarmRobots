using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class SpawnAreas : MonoBehaviour
{
    public bool showSpawnAreas;
    private List<Vector3> spawnAreaSizes;
    private List<Vector3> spawnAreaPositions;

    // Start is called before the first frame update
    void Awake()
    {
        spawnAreaSizes = new List<Vector3>();
        spawnAreaPositions = new List<Vector3>();
        foreach (Transform child in transform)
        {
            Vector3 spawnSize = child.GetComponent<Renderer>().bounds.size;

            spawnAreaSizes.Add(spawnSize);
            spawnAreaPositions.Add(child.localPosition);
        }

        Renderer[] rs = GetComponentsInChildren<Renderer>();
        foreach (Renderer r in rs)
            r.enabled = showSpawnAreas;
    }


    public Vector3 GetRndPosition()
    {
        int rndIndex = Random.Range(0, spawnAreaSizes.Count);
        Vector3 spawnSize = spawnAreaSizes[rndIndex];
        Vector3 rndPosition = new(
            Random.value * spawnSize.x - spawnSize.x / 2,
            1.5f,
            Random.value * spawnSize.z - spawnSize.z / 2);
        return rndPosition + spawnAreaPositions[rndIndex];
    }

}
