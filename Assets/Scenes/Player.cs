using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Player : MonoBehaviour
{

    private Animator anim;
    private Rigidbody rigid;
    public float JumpForce = 500;
    public float groundDistance = 0.3f;
    public LayerMask whatIsGround;

    void Start()
    {
        anim = GetComponent<Animator>();
        rigid = GetComponent<Rigidbody>();
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
        }
        if(Physics.Raycast(transform.position+(Vector3.up*0.1f),Vector3.down,groundDistance,whatIsGround)){
            anim.SetBool("grounded",true);
            anim.applyRootMotion = true;
        }
        else{
            anim.SetBool("grounded",false);
        }
    }
}
