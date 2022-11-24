using System.Collections.Generic;
using System.Linq;
using UnityEngine;

public class SelectRandomMaze : MonoBehaviour
{
    public List<Transform> randomMazes = new();

    private void Awake()
    {
        foreach (Transform child in transform)
        {
            randomMazes.Add(child);
        }

        randomlySelectMaze();
    }

    private void randomlySelectMaze()
    {
        if (randomMazes.Count == 0) return;
        var rand = Random.Range(0, randomMazes.Count);

        foreach (var maze in randomMazes)
        {
            maze.gameObject.SetActive(maze == randomMazes[rand].transform);
        }
    }

    public Transform getActiveMaze()
    {
        randomlySelectMaze();
        // iterate through all first level children
        var result = randomMazes
            .FirstOrDefault(child => child.gameObject.activeSelf);
        return result;
    }
}