using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Player : MonoBehaviour
{

    private Animator anim;
    private Rigidbody rigid;
    public float JumpForce = 1000;
    public float groundDistance = 0.3f;
    public LayerMask whatIsGround;

    void Start()
    {
        anim = GetComponent<Animator>();
        rigid = GetComponent<Rigidbody>();
        anim.SetBool("grounded", true);
    }

    // Update is called once per frame
    void Update()
    {
        var v = Input.GetAxis("Vertical");
        var h = Input.GetAxis("Horizontal");
        anim.SetFloat("speed",v);
        anim.SetFloat("Turningspeed",h);
        
        
        if(Input.GetButtonDown("Jump")){
            rigid.AddForce(Vector3.up * JumpForce);
            anim.SetTrigger("Jump");
            Debug.Log("여기냐?");
            anim.SetBool("grounded",false);
        }
        else if(anim.GetComponent("grounded") == false && Physics.Raycast(transform.position+(Vector3.up*0.1f),Vector3.down,groundDistance,whatIsGround)){
            anim.SetBool("grounded",true);
            anim.applyRootMotion = true;
            Debug.Log("3423");
        }
        else{
            anim.SetBool("grounded",true);
        }

        Debug.Log(anim.GetComponent("grounded"));
        if(anim.GetComponent("grounded") == false){
            anim.SetFloat("speed",0);
            anim.SetFloat("Turningspeed",0);
            Debug.Log("asdf");
        }
    }
}
