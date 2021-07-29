#ifndef XTRACK_TRACKER_H
#define XTRACK_TRACKER_H

#ifdef XTRACK_GLOBAL_POSLIMIT

/*gpufun*/
void global_aperture_check(LocalParticle* part0){


    //start_per_particle_block
        double const x = LocalParticle_get_x(part);
        double const y = LocalParticle_get_y(part);

	int64_t const is_alive = (int64_t)(
                      (x >= -XTRACK_GLOBAL_POSLIMIT) &&
		      (x <=  XTRACK_GLOBAL_POSLIMIT) &&
		      (y >= -XTRACK_GLOBAL_POSLIMIT) &&
		      (y <=  XTRACK_GLOBAL_POSLIMIT) );

	// I assume that if I am in the function is because
    	if (!is_alive){
           LocalParticle_set_state(part, 0);
	}
    //end_per_particle_block


}
#endif

/*gpufun*/
void increment_at_element(LocalParticle* part0){

   //start_per_particle_block
        LocalParticle_add_to_at_element(part, 1);
   //end_per_particle_block


}

/*gpufun*/
void increment_at_turn(LocalParticle* part0){

    //start_per_particle_block
	LocalParticle_set_at_element(part, 0);
    //end_per_particle_block
}


// check_is_not_lost has different implementation on CPU and GPU

#define CPUIMPLEM //only_for_context cpu_serial cpu_openmp

#ifdef CPUIMPLEM

/*gpufun*/
int64_t check_is_not_lost(LocalParticle* part) {
    int64_t ipart=0;
    while (ipart < part->num_particles){
        if (part->state[ipart]<1){
            LocalParticle_exchange(part, ipart, part->num_particles-1);
            part->num_particles--; 
        }
	else{
	    ipart++;
	}
    }

    if (part->num_particles==0){
        return 0;//All particles lost
    } else {
        return 1; //Some stable particles are still present
    }
}

#else

/*gpufun*/
int64_t check_is_not_lost(LocalParticle* part) {
    return LocalParticle_get_state(part);
};

#endif

#undef CPUIMPLEM //only_for_context cpu_serial cpu_openmp

#endif
