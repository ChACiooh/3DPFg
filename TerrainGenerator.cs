using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.IO;
public class TerrainGenerator : MonoBehaviour
{
    public int depth = 20;
    public int width = 64;
    public int map_width = 50;
    public int height = 64;
    public int map_height = 50;
    public StreamReader sr;
    public float[,] heights;
    public float[,] heights_new;
    public int mapNum;

    void Start(){
        heights = new float[map_width, map_height];
        heights_new = new float[width, height];
        reader();
    }
    void Update(){
        Terrain terrain = GetComponent<Terrain>();
        terrain.terrainData = GenerateTerrain(terrain.terrainData);

    }
    public void reader(){
        string filepth = "Assets/terrainData/map_info_"+mapNum;
        sr = new StreamReader(filepth + ".json");
        
        bool endOfFile = false;
        while(!endOfFile){
            for(int x = 0; x < map_width; x++){
                for(int z = 0; z < map_height; z++){
                    string data_String = sr.ReadLine();
                    while(data_String.Contains("[") || data_String.Contains("]")){
                        data_String = sr.ReadLine();
                    }
                    if(data_String == null){
                        endOfFile = true;
                        break;
                    }
                    var data_values = data_String.Split(',');
                    heights_new[x,z] = heights[x,z] = float.Parse(data_values[0]) / depth;
                    //Debug.Log("heights["+x+","+z+"]"+heights[x,z]);
                    
                }

                // padding
                for(int z = map_height; z < height; z++) {
                    heights_new[x, z] = 0f;
                }
            }
            
            for(int x = map_width; x < width; x++) {
                for(int z = 0; z < height; ++z) {
                    heights_new[x, z] = 0f;
                }
            }
        }        
    }
    TerrainData GenerateTerrain(TerrainData terrainData){
        terrainData.heightmapResolution = width + 1;
        // Debug.Log("getlength"+heights_new.GetLength(0));
        terrainData.size = new Vector3(width, depth, height);
        terrainData.SetHeights(0,0,heights_new);
        return terrainData;
    }

}
