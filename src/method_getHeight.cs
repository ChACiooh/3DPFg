        public virtual void getHeights(){
            int xSize = 10, zSize = 10;
            float[,] heights_at_position = new float[xSize, zSize];
            //Debug.Log("vThirdPersonInput.cs-getHeights() called.");
            Vector3 dir_vec = cc.transform.position - tpCamera.transform.position;
            dir_vec = dir_vec.normalized;

            float mapX = cc.transform.position.x;
            float mapZ = cc.transform.position.z;
            float dx = dir_vec.x, dz = dir_vec.z;

            System.String str_debug = "";
            for(int i = 0; i < 10; ++i) {
                for(int j = 0; j < 10; ++j) {
                    heights_at_position[i,j] = terrainData.GetHeight((int)(mapX + i * dx), (int)(mapZ + j * dz));
                    str_debug += System.String(heights_at_position[i, j]) + " ";
                }
                str_debug += "\n";
            }
            
            Debug.Log(str_debug);
        }