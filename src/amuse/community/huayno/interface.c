#include <stdio.h>
#include <stdlib.h>
#include "evolve.h"
// AMUSE STOPPING CONDITIONS SUPPORT
#include <stopcond.h>

#include "simple_map.h"
#include "simple_hash.h"

#define NMAX 10000
static struct sys mainsys;

static int nmax;

static int pcounter;
static double t_now;
static int inttype;
static double dtime;
static double begin_time = 0;

// for pedagogical reasons: map can be changed to hash or vv
#define  LOOKUPSYMBOL(x,y)  x##hash##y
struct LOOKUPSYMBOL(simple_,) lookup;

int initialize_code()
{
  pcounter=0;
  nmax=NMAX;
  LOOKUPSYMBOL(init_,)(&lookup, nmax*sizeof(struct particle)/sizeof(int));
  mainsys.n=0;
  mainsys.part=(struct particle*) malloc(nmax*sizeof(struct particle));
  mainsys.last=NULL;
  dt_param=.03; 
  eps2=0.;
  inttype=8;
  dtime=0.;
  init_code();
  // AMUSE STOPPING CONDITIONS SUPPORT
  set_support_for_condition(COLLISION_DETECTION);
  return 0;
}

int cleanup_code()
{ 
    pcounter=0;
    LOOKUPSYMBOL(clear_,)(&lookup);
    mainsys.n=0;
    free(mainsys.part);
    mainsys.last=NULL;
    dt_param=.03; 
    dtime=0.;
    eps2=0.;
    inttype=8;
    begin_time = 0;
    stop_code();
    return 0;
}

int new_particle(int *id, double mass,
                 double x, double y, double z,
                 double vx, double vy, double vz,
                 double radius)
{
 int p,err;
 p=mainsys.n;
 if(p>=nmax)
 {
   struct particle *new;
   nmax*=2;
   new=(struct particle *) realloc( mainsys.part, nmax*sizeof(struct particle) );  
   if(new == NULL) return -1;
   mainsys.part=new;
 }
 *id=pcounter;
 err=LOOKUPSYMBOL(,_insert)(&lookup,*id,p);
 if(err!=0) return err;
 mainsys.part[p].id=*id;
 mainsys.part[p].mass=mass;
 mainsys.part[p].radius=radius;
 mainsys.part[p].pos[0]=x;
 mainsys.part[p].pos[1]=y;
 mainsys.part[p].pos[2]=z;
 mainsys.part[p].vel[0]=vx;
 mainsys.part[p].vel[1]=vy;
 mainsys.part[p].vel[2]=vz;
 mainsys.part[p].pot=0.;
 mainsys.part[p].timestep=0.;
 mainsys.part[p].postime=0;
 mainsys.n++;
 pcounter++;
 mainsys.last=&mainsys.part[p];
 return 0;
}

int delete_particle(int id)
{
  size_t p;
  int err;
  err=LOOKUPSYMBOL(,_lookup)(&lookup, id,&p);
  if(err!=0) return err;
  LOOKUPSYMBOL(,_delete)(&lookup,id);  
  mainsys.n--;
  if(mainsys.n==0)
  {
    mainsys.last=NULL;
    return 0;
  }
  mainsys.last--;
  mainsys.part[p]=mainsys.part[mainsys.n];
  LOOKUPSYMBOL(,_update)(&lookup,mainsys.part[p].id,p);
  return 0; 
}
                 
int get_state(int id, double *mass,
        double *x, double *y, double *z,
        double *vx, double *vy, double *vz,
        double *radius)
{
  size_t p;
  int err;
  err=LOOKUPSYMBOL(,_lookup)( &lookup, id,&p);
  if(err!=0) return err;
 *mass=mainsys.part[p].mass; 
 *radius=mainsys.part[p].radius;
 *x=mainsys.part[p].pos[0]; 
 *y=mainsys.part[p].pos[1]; 
 *z=mainsys.part[p].pos[2]; 
 *vx=mainsys.part[p].vel[0]; 
 *vy=mainsys.part[p].vel[1]; 
 *vz=mainsys.part[p].vel[2]; 
 return 0;
}

int get_mass(int id, double *mass)
{
  size_t p;
  int err;
  err=LOOKUPSYMBOL(,_lookup)( &lookup, id,&p);
  if(err!=0) return err;
 *mass=mainsys.part[p].mass; 
 return 0;
}

int get_radius(int id, double *radius)
{
  size_t p;
  int err;
  err=LOOKUPSYMBOL(,_lookup)( &lookup, id,&p);
  if(err!=0) return err;
 *radius=mainsys.part[p].radius;
 return 0;
}

int get_position(int id, double *x, double *y, double *z)
{
  size_t p;
  int err;
  err=LOOKUPSYMBOL(,_lookup)( &lookup, id,&p);
  if(err!=0) return err;
 *x=mainsys.part[p].pos[0]; 
 *y=mainsys.part[p].pos[1]; 
 *z=mainsys.part[p].pos[2]; 
 return 0;
}

int get_velocity(int id, double *vx, double *vy, double *vz)
{
  size_t p;
  int err;
  err=LOOKUPSYMBOL(,_lookup)( &lookup, id,&p);
  if(err!=0) return err;
 *vx=mainsys.part[p].vel[0]; 
 *vy=mainsys.part[p].vel[1]; 
 *vz=mainsys.part[p].vel[2]; 
 return 0;
}

int set_state(int id, double mass, 
        double x, double y, double z,
        double vx, double vy, double vz, 
        double radius)
{
  size_t p;
  int err;
  err=LOOKUPSYMBOL(,_lookup)( &lookup, id,&p);
  if(err!=0) return err;
  mainsys.part[p].mass=mass; 
  mainsys.part[p].radius=radius; 
  mainsys.part[p].pos[0]=x; 
  mainsys.part[p].pos[1]=y; 
  mainsys.part[p].pos[2]=z; 
  mainsys.part[p].vel[0]=vx; 
  mainsys.part[p].vel[1]=vy; 
  mainsys.part[p].vel[2]=vz; 
  return 0;
}

int set_mass(int id, double mass)
{
  size_t p;
  int err;
  err=LOOKUPSYMBOL(,_lookup)( &lookup, id,&p);
  if(err!=0) return err;
  mainsys.part[p].mass=mass; 
  return 0;
}

int set_radius(int id, double radius)
{
  size_t p;
  int err;
  err=LOOKUPSYMBOL(,_lookup)( &lookup, id,&p);
  if(err!=0) return err;
  mainsys.part[p].radius=radius; 
  return 0;
}


int set_position(int id, double x, double y, double z)
{
  size_t p;
  int err;
  err=LOOKUPSYMBOL(,_lookup)( &lookup, id,&p);
  if(err!=0) return err;
  mainsys.part[p].pos[0]=x; 
  mainsys.part[p].pos[1]=y; 
  mainsys.part[p].pos[2]=z;  
  return 0;
}

int set_velocity(int id, double vx, double vy, double vz)
{
  size_t p;
  int err;
  err=LOOKUPSYMBOL(,_lookup)( &lookup, id,&p);
  if(err!=0) return err;
  mainsys.part[p].vel[0]=vx; 
  mainsys.part[p].vel[1]=vy; 
  mainsys.part[p].vel[2]=vz; 
  return 0;
}

int get_number_of_particles(int  *n)
{
  *n=mainsys.n;
  return 0;
}

int get_index_of_first_particle(int  *id)
{
  if(mainsys.n <=0) return 1;
  *id=mainsys.part[0].id;
  return 0;
}

int get_index_of_next_particle(int  id, int *nout)
{
  size_t p;
  int err;
  err=LOOKUPSYMBOL(,_lookup)( &lookup, id,&p);
  if(err!=0) return err;
  if(p ==mainsys.n-1) return 1;
  *nout=mainsys.part[p+1].id;
  return 0;
}
             
int get_kinetic_energy(double *kinetic_energy)
{
  *kinetic_energy=system_kinetic_energy(mainsys);
  return 0;
}

int get_potential_energy(double *potential_energy)
{
  *potential_energy=system_potential_energy(mainsys);
  return 0;
}

int get_inttype_parameter(int *i)
{
  *i=inttype;
  return 0;
}

int set_inttype_parameter(int i)
{
  inttype=i;
  return 0;
}

int set_timestep_parameter(double t)
{
  dt_param=t;
  return 0;
}

int get_timestep_parameter(double *t)
{
  *t=dt_param;
  return 0;
}

int set_timestep(double t)
{
  dtime=t;
  return 0;
}

int get_timestep(double *t)
{
  *t=dtime;
  return 0;
}

int evolve_model(double t_end)
{
  double dt=SIGN(t_end-t_now)*dtime;
  if(dt==0.) dt=t_end-t_now;
  reset_stopping_conditions();
  while(SIGN(dt)*(t_end - t_now) > SIGN(dt)*dt/2) 
  {
    if(mainsys.n > 0) do_evolve(mainsys,dt,inttype);
    if (set_conditions & enabled_conditions) {
      printf("Stopping condition set!\n");
      break;
    } else {
      t_now+=dt;
    }
  }
  for(int p=0;p<mainsys.n;p++) LOOKUPSYMBOL(,_update)(&lookup, mainsys.part[p].id,p);

  if (set_conditions & enabled_conditions) {
    int err,type, number_of_particles, id;
    size_t p;
    // COLLISION_DETECTION is currently the only supported stopping condition,
    // so we know that the first one set should be a collision:
    err=get_stopping_condition_info(0, &type, &number_of_particles);
    if ((err < 0) || (type != COLLISION_DETECTION)) {
      printf("get_stopping_condition_info error: %d\n", err);
      return -1;
    }
    get_stopping_condition_particle_index(0, 0, &id);
    LOOKUPSYMBOL(,_lookup)( &lookup, id,&p);
    t_now += mainsys.part[p].postime;
  }

  return 0;
}

int get_time(double *time)
{
 *time=t_now;
 return 0;
}

int set_begin_time(double input) {
    begin_time = input;
    return 0;
}

int get_begin_time(double * output) {
    *output = begin_time;
    return 0;
}

int commit_particles()
{
  init_evolve(mainsys,inttype);
  return 0;
}

int set_eps2_parameter(double e)
{
  eps2=e;
  return 0;
}

int get_eps2_parameter(double *e)
{
  *e=eps2;
  return 0;
}

int set_timestep_option(int ts)
{
  return 0;
}

int get_timestep_option(int *ts)
{
  *ts=0;
  return 0;
}

int synchronize_model()
{
  return 0;
}

int recommit_particles()
{
  init_evolve(mainsys,inttype);
  return 0;
}

int get_time_step(double *dt)
{
  return -1;
}

int get_total_mass(double *m)
{
  int p;
  for(*m=0,p=0;p<mainsys.n;p++) *m+=mainsys.part[p].mass;
  return 0;
}

int get_total_radius(double *r)
{
  return -2;
}

int get_center_of_mass_position(double *x,double *y,double *z)
{
  return -2;
}

int get_center_of_mass_velocity(double *vx,double *vy,double *vz)
{
  return -2;
}

int recommit_parameters()
{
  init_evolve(mainsys,inttype);
  return 0;
}
int commit_parameters()
{
    t_now = begin_time;
    return 0;
}

int get_potential(int id, double *pot)
{
  size_t p;
  int err;
  err=LOOKUPSYMBOL(,_lookup)( &lookup, id,&p);
  if(err!=0) return err;
  *pot=mainsys.part[p].pot;
  return 0;
}

int set_acceleration(int id, double ax, double ay, double az)
{
  return -2;
}

int get_acceleration(int id, double *ax, double *ay, double *az)
{
  return -2;
}

int get_indices_of_colliding_particles(int *p1,int*p2)
{
  return -2;
}  

int get_gravity_at_point(double * eps, double * x, double * y, double * z, 
			 double * ax, double * ay, double * az, int n)
{
  struct sys tmpsys;
  tmpsys.n=n;
  tmpsys.part=(struct particle*) malloc(n*sizeof(struct particle));
  tmpsys.last=&tmpsys.part[n];
  for(int p=0;p<n;p++)
  {
    tmpsys.part[p].pos[0]=x[p];
    tmpsys.part[p].pos[1]=y[p];
    tmpsys.part[p].pos[2]=z[p];
    tmpsys.part[p].vel[0]=0;
    tmpsys.part[p].vel[1]=0;
    tmpsys.part[p].vel[2]=0;
#ifdef COMPENSATED_SUMMV
    tmpsys.part[p].vel_e[0]=0;
    tmpsys.part[p].vel_e[1]=0;
    tmpsys.part[p].vel_e[2]=0;  
#endif
    tmpsys.part[p].radius=eps[p]; /* not used */
  }
  kick(0,tmpsys,mainsys,1.);
  for(int p=0;p<n;p++) 
  {
    ax[p]=tmpsys.part[p].vel[0];
    ay[p]=tmpsys.part[p].vel[1];
    az[p]=tmpsys.part[p].vel[2];
  }
  free(tmpsys.part);
  return 0;
}

int get_potential_at_point(double * eps,
			   double * x, double * y, double * z, 
			   double * phi, int n)
{
  struct sys tmpsys;
  tmpsys.n=n;
  tmpsys.part=(struct particle*) malloc(n*sizeof(struct particle));
  tmpsys.last=&tmpsys.part[n];
  for(int p=0;p<n;p++)
  {
    tmpsys.part[p].pos[0]=x[p];
    tmpsys.part[p].pos[1]=y[p];
    tmpsys.part[p].pos[2]=z[p];
    tmpsys.part[p].radius=eps[p]; /* not used */
    tmpsys.part[p].pot=0;
  }
  potential(tmpsys,mainsys);
  for(int p=0;p<n;p++) phi[p]=tmpsys.part[p].pot;
  free(tmpsys.part);
  return 0;
}

int get_evolve_statistics(long int *ttot,long int *ktot,long int *dtot,long int *tstot,long int *kstot,long int *dstot)
{
  *ttot=0; *ktot=0; *dtot=0;
  *tstot=0; *kstot=0; *dstot=0;
  for(int i = 0; i < MAXLEVEL; i++)
  {
    *ttot += diag->tcount[i];
    *ktot += diag->kcount[i];
    *dtot += diag->dcount[i];
    *tstot += diag->tstep[i];
    *kstot += diag->kstep[i];
    *dstot += diag->dstep[i];
  }
  return 0;
}
