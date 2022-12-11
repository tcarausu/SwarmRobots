using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;

public class SceneChanger : MonoBehaviour
{
	public enum MazeSize
    {
		Toy,
		Small,
		Medium,
		Big
    }

	public MazeSize size;

	private bool sceneChanging = false;

	public void EndScene()
	{
		if (size == MazeSize.Big)
		{
			Application.Quit();
#if UNITY_EDITOR
			UnityEditor.EditorApplication.isPlaying = false;
#endif
        }
        else
        {	
			MazeSize nextSize = size + 1;
			string newSceneName = nextSize.ToString() + "MazeTest";
			SceneManager.LoadScene(newSceneName);
			sceneChanging = true;

		}
	}
	public void Exit()
	{
		Application.Quit();
	}

	public bool isSceneChanging()
    {
		return sceneChanging;
    }
}
