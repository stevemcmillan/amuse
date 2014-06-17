from amuse.test.amusetest import TestWithMPI
import sys
import os.path
from numpy import pi, arange
import numpy.random

from amuse.community.evtwin.interface import EVtwin, EVtwinInterface

from amuse.support.exceptions import AmuseException
from amuse.units import nbody_system, units
from amuse.units.quantities import new_quantity
from amuse.datamodel import Particle, Particles
from amuse.rfi import channel


class TestEVtwinInterface(TestWithMPI):
    
    def test1(self):
        instance = EVtwinInterface()
#~        error = instance.set_ev_path(instance.get_data_directory())
#~        self.assertEquals(0, error)
        error = instance.initialize_code()
        self.assertEquals(0, error)
        error = instance.cleanup_code()
        self.assertEquals(0, error)
        instance.stop()
    
    def test2(self):
        instance = EVtwinInterface()
        error = instance.initialize_code()
        self.assertEquals(0, error)
        error = instance.set_ev_path(instance.get_data_directory())
        self.assertEquals(0, error)
        error = instance.cleanup_code()
        self.assertEquals(0, error)
        instance.stop()
    
    def test3(self):
        print "Testing get/set for metallicity..."
        instance = EVtwinInterface()
        error = instance.initialize_code()
        self.assertEquals(0, error)
        error = instance.set_ev_path(instance.get_data_directory())
        self.assertEquals(0, error)
        (metallicity, error) = instance.get_metallicity()
        self.assertEquals(0, error)
        self.assertEquals(0.02, metallicity)
        
        # Z > 0.04 is not allowed
        error = instance.set_metallicity(0.0401)
        self.assertEquals(0, error)
        error = instance.commit_parameters()
        self.assertEquals(-2, error)
        
        # 0.0 <= Z <= 0.04 is allowed
        any_allowed_Z = numpy.random.random() * 0.04
        error = instance.set_metallicity(any_allowed_Z)
        self.assertEquals(0, error)
        (metallicity, error) = instance.get_metallicity()
        self.assertEquals(0, error)
        self.assertEquals(any_allowed_Z, metallicity)
        error = instance.commit_parameters()
        self.assertEquals(0, error)
        error = instance.cleanup_code()
        self.assertEquals(0, error)
        instance.stop()
    
    def test4(self):
        print "Testing get/set for maximum number of stars..."
        instance = EVtwinInterface()
        error = instance.initialize_code()
        self.assertEquals(0, error)
        error = instance.set_ev_path(instance.get_data_directory())
        self.assertEquals(0, error)
        (value, error) = instance.get_maximum_number_of_stars()
        self.assertEquals(0, error)
        self.assertEquals(10, value)
        
        error = instance.set_maximum_number_of_stars(10000)
        self.assertEquals(0, error)      
        
        (value, error) = instance.get_maximum_number_of_stars()
        self.assertEquals(0, error)      
        self.assertEquals(10000, value)      
        
        error = instance.commit_parameters()
        self.assertEquals(0, error)
        error = instance.cleanup_code()
        self.assertEquals(0, error)
        instance.stop()
    
    
    def test5(self):
        print "Testing basic operations (new_particle, evolve_one_step etc.)..."
        instance = EVtwinInterface()
        error = instance.initialize_code()
        self.assertEquals(0, error)
        error = instance.set_ev_path(instance.get_data_directory())
        self.assertEquals(0, error)
        error = instance.commit_parameters()
        self.assertEquals(0, error)
        
        (index_of_the_star, error) = instance.new_particle(1.05)
        self.assertEquals(0, error)
        self.assertTrue(index_of_the_star >= 0)
        error = instance.commit_particles()
        self.assertEquals(0, error)
        error = instance.set_wind_multiplier(index_of_the_star, 1.0)
        self.assertEquals(0, error)
        
        (mass, error) = instance.get_mass(index_of_the_star)
        self.assertEquals(0, error)
        self.assertEquals(1.05, mass)
        
        for i in range(3):
            error = instance.evolve_one_step(index_of_the_star)
            self.assertEquals(0, error)
    
        (mass, error) = instance.get_mass(index_of_the_star)
        self.assertEquals(0, error)
        self.assertTrue(mass <= 1.05)
    
        (age, error) = instance.get_age(index_of_the_star)
        self.assertEquals(0, error)
        self.assertTrue(age > 0)
        
        (x, error) = instance.get_wind_mass_loss_rate(index_of_the_star)
        self.assertEquals(0, error)
        self.assertTrue(x < 1e-13, "mass loss should be less than 1e-13, it is {0}".format(x))
        self.assertTrue(x > 0, "mass loss rate should be more than 0, it is {0}".format(x))
        
        error = instance.cleanup_code()
        self.assertEquals(0, error)
        instance.stop()
        
    def test6(self):
        print "Testing EVtwin stop conditions..."
        instance = EVtwinInterface()
        error = instance.initialize_code()
        self.assertEquals(0, error)      
        error = instance.set_ev_path(instance.get_data_directory())
        self.assertEquals(0, error)      
                
        (value, error) = instance.get_max_age_stop_condition()
        self.assertEquals(0, error)
        self.assertEquals(1.0e12, value)
        for x in range(10,14):
            error = instance.set_max_age_stop_condition(10 ** x)
            self.assertEquals(0, error)
            (value, error) = instance.get_max_age_stop_condition()
            self.assertEquals(0, error)      
            self.assertEquals(10 ** x, value)
            
        (value, error) = instance.get_min_timestep_stop_condition()
        self.assertEquals(0, error)
        self.assertAlmostEqual(1.0e6, value, 5)
        for x in range(-3,2):
            error = instance.set_min_timestep_stop_condition(10 ** x)
            self.assertEquals(0, error)
            (value, error) = instance.get_min_timestep_stop_condition()
            self.assertEquals(0, error)
            self.assertEquals(10 ** x, value)
        
        instance.stop()

    def test7(self):
        print "Testing EVtwin parameters..."
        instance = EVtwinInterface()
        error = instance.initialize_code()
        self.assertEquals(0, error)      
        error = instance.set_ev_path(instance.get_data_directory())
        self.assertEquals(0, error)      
        error = instance.commit_parameters()
        self.assertEquals(0, error)
        
        (value, error) = instance.get_number_of_ionization_elements()
        self.assertEquals(0, error)
        self.assertEquals(5, value)
        for x in range(1,10):
            error = instance.set_number_of_ionization_elements(x)
            self.assertEquals(0, error)
            (value, error) = instance.get_number_of_ionization_elements()
            self.assertEquals(0, error)
            self.assertEquals(x, value)

        (value, error) = instance.get_convective_overshoot_parameter()
        self.assertEquals(0, error)
        self.assertEquals(0.12, value)
        for x in [0.0, 0.1, 0.12, 0.15]:
            error = instance.set_convective_overshoot_parameter(x)
            self.assertEquals(0, error)
            (value, error) = instance.get_convective_overshoot_parameter()
            self.assertEquals(0, error)
            self.assertEquals(x, value)

        (value, error) = instance.get_mixing_length_ratio()
        self.assertEquals(0, error)
        self.assertEquals(2.0, value)
        for x in [0.1, 1.0, 3.0]:
            error = instance.set_mixing_length_ratio(x)
            self.assertEquals(0, error)
            (value, error) = instance.get_mixing_length_ratio()
            self.assertEquals(0, error)
            self.assertEquals(x, value)

        (value, error) = instance.get_semi_convection_efficiency()
        self.assertEquals(0, error)
        self.assertEquals(0.04, value)
        for x in [0.0, 0.1]:
            error = instance.set_semi_convection_efficiency(x)
            self.assertEquals(0, error)
            (value, error) = instance.get_semi_convection_efficiency()
            self.assertEquals(0, error)
            self.assertEquals(x, value)
        
        (value, error) = instance.get_thermohaline_efficiency()
        self.assertEquals(0, error)
        self.assertEquals(1.0, value)
        for x in [0.0, 0.5, 1.5]:
            error = instance.set_thermohaline_efficiency(x)
            self.assertEquals(0, error)
            (value, error) = instance.get_thermohaline_efficiency()
            self.assertEquals(0, error)
            self.assertEquals(x, value)
        
        instance.stop()
    
    def test9(self):
        print "Testing adding and removing particles from stellar evolution code..."
        instance = EVtwinInterface()
        self.assertEquals(0, instance.initialize_code())
        self.assertEquals(0, instance.set_ev_path(instance.get_data_directory()))
        self.assertEquals(0, instance.commit_parameters())
        
        (indices, errors) = instance.new_particle([1.0, 1.0])
        self.assertEquals(errors, [0, 0])
        self.assertEquals(indices, [1, 2])
        
        self.assertEquals(0, instance.commit_particles())
        

        for index in indices:
            self.assertEquals(0, instance.evolve_one_step(index))
            (age_after_evolve, error) = instance.get_age(index)
            self.assertEquals(0, error)
            self.assertAlmostEqual(age_after_evolve, 9000000.0, 5)
        
        self.assertEquals(0, instance.delete_star(1))
        self.assertEquals(instance.get_number_of_particles()['number_of_particles'], 1)
        (age, error) = instance.get_age(1)
        self.assertEquals(error, -1)
        
        (indices, errors) = instance.new_particle([1.0, 1.0])
        self.assertEquals(errors, [0, 0])
        self.assertEquals(indices, [1, 3])
        self.assertEquals(instance.get_number_of_particles()['number_of_particles'], 3)
        
        for index in indices:
            (age, error) = instance.get_age(index)
            self.assertEquals(0, error)
            print age, age_after_evolve
            self.assertTrue(age < age_after_evolve)
            self.assertEquals(0, instance.evolve_one_step(index))
            (age, error) = instance.get_age(index)
            self.assertEquals(0, error)
#~            self.assertAlmostEqual(age, age_after_evolve)
        
        instance.stop()
    

class TestEVtwin(TestWithMPI):
    
            
    
    def test0(self):
        instance = EVtwin()
        instance.initialize_code()
        instance.cleanup_code()
        instance.stop()
    
    def test1(self):
        print "Testing assigned default parameter values..."
        instance = EVtwin()
        instance.initialize_code()
        instance.parameters.set_defaults()
        self.assertEquals(10, instance.parameters.maximum_number_of_stars)
        instance.parameters.maximum_number_of_stars = 12 
        self.assertEquals(12, instance.parameters.maximum_number_of_stars)
        instance.stop()
    
    def xtest2(self):
        print "Testing basic operations"
        instance = EVtwin()
        instance.initialize_code()
        instance.commit_parameters()
        
        stars = Particles(1)
        stars.mass = 10 | units.MSun
        
        instance.particles.add_particles(stars)
        instance.commit_particles()
        instance.particles.copy_values_of_all_attributes_to(stars)
        
        self.assertEquals(stars.mass, 10 | units.MSun)
        self.assertAlmostEquals(stars.luminosity, 5695.19757302 | units.LSun, 6)
        instance.stop()
    
    def xtest3(self):
        instance = EVtwin()
        instance.initialize_code()
        instance.commit_parameters()
        stars = Particles(1)
        
        star = stars[0]
        star.mass = 5.0 | units.MSun
        star.radius = 0.0 | units.RSun
        
        instance.particles.add_particles(stars)
        instance.commit_particles()
        
        from_code_to_model = instance.particles.new_channel_to(stars)
        from_code_to_model.copy()
        
        previous_type = star.stellar_type
        results = []
        t0 = 0 | units.Myr
        current_time = t0
        
        while current_time < (115 | units.Myr):
            instance.evolve_model()
            from_code_to_model.copy()
            
            current_time = star.age
            print (star.age, star.mass, star.stellar_type)
            if not star.stellar_type == previous_type:
                results.append((star.age, star.mass, star.stellar_type))
                previous_type = star.stellar_type
        
        print results
        self.assertEqual(len(results), 6)
        
        times = ( 
            104.0 | units.Myr, 
            104.4 | units.Myr, 
            104.7 | units.Myr, 
            120.1 | units.Myr,
            120.9 | units.Myr,
            121.5 | units.Myr
        )
        for result, expected in zip(results, times):
            self.assertAlmostEqual(result[0].value_in(units.Myr), expected.value_in(units.Myr), 1)
            
        masses = ( 
            5.000 | units.MSun, 
            5.000 | units.MSun, 
            4.998 | units.MSun, 
            4.932 | units.MSun,
            4.895 | units.MSun,
            0.997 | units.MSun
        )
        for result, expected in zip(results, masses):
            self.assertAlmostEqual(result[1].value_in(units.MSun), expected.value_in(units.MSun), 3)
         
        types = (
            "Hertzsprung Gap",
            "First Giant Branch",
            "Core Helium Burning",
            "First Asymptotic Giant Branch",
            "Second Asymptotic Giant Branch",
            "Carbon/Oxygen White Dwarf",
        )
        
        for result, expected in zip(results, types):
            self.assertEquals(str(result[2]), expected)
        
        instance.stop()
        
    def xtest4(self):
        print "Testing max age stop condition..."
        #masses = [.5, 1.0, 1.5] | units.MSun # Test with fewer particles for speed-up.
        masses = [.5] | units.MSun
        max_age = 9.0 | units.Myr

        number_of_stars=len(masses)
        stars = Particles(number_of_stars)
        for i, star in enumerate(stars):
            star.mass = masses[i]
            star.radius = 0.0 | units.RSun

#       Initialize stellar evolution code
        instance = EVtwin() #debugger="xterm")
        instance.initialize_code()
        if instance.get_maximum_number_of_stars() < number_of_stars:
            instance.set_maximum_number_of_stars(number_of_stars)
        self.assertEqual(instance.parameters.max_age_stop_condition, 2e6 | units.Myr)
        instance.parameters.max_age_stop_condition = max_age
        self.assertEqual(instance.parameters.max_age_stop_condition, max_age)
        instance.commit_parameters()
        instance.particles.add_particles(stars)
#       Let the code perform initialization actions after all particles have been created. 
        instance.commit_particles()
        
        from_code_to_model = instance.particles.new_channel_to(stars)
        from_code_to_model.copy()
        
        instance.evolve_model(end_time = 8.0 | units.Myr)
        from_code_to_model.copy()
        
        for i in range(number_of_stars):
            print stars[i].age.as_quantity_in(units.Myr)
            self.assertTrue(stars[i].age.value_in(units.Myr) >= 8.0)
            self.assertTrue(stars[i].age <= max_age)
            self.assertTrue(stars[i].mass <= masses[i])
            self.assertTrue(stars[i].time_step <= max_age)
                
        self.assertRaises(AmuseException, instance.evolve_model, end_time = 2*max_age, 
            expected_message = "Error when calling 'evolve_for' of a 'EVtwin', errorcode "
                "is 5, error is 'PRINTB -- age greater than limit'")

        instance.stop()

    def xtest4b(self):
        print "Testing alternate max age stop condition..."
        masses = [.5] | units.MSun
        max_age = 12.0 | units.Myr

        number_of_stars=len(masses)
        stars = Particles(number_of_stars)
        for i, star in enumerate(stars):
            star.mass = masses[i]
            star.radius = 0.0 | units.RSun

#       Initialize stellar evolution code
        instance = EVtwin() #debugger="xterm")
        self.assertEqual(instance.parameters.max_age_stop_condition, 2e6 | units.Myr)
        instance.parameters.max_age_stop_condition = max_age
        self.assertEqual(instance.parameters.max_age_stop_condition, max_age)
        instance.particles.add_particles(stars)
#       Let the code perform initialization actions after all particles have been created. 
        
        from_code_to_model = instance.particles.new_channel_to(stars)
        from_code_to_model.copy()
        
        instance.evolve_model(end_time = 8.0 | units.Myr)
        from_code_to_model.copy()
        
        for i in range(number_of_stars):
            print stars[i].age.as_quantity_in(units.Myr)
            self.assertTrue(stars[i].age.value_in(units.Myr) >= 8.0)
            self.assertTrue(stars[i].age <= max_age)
            self.assertTrue(stars[i].mass <= masses[i])
            self.assertTrue(stars[i].time_step <= max_age)
                
        self.assertRaises(AmuseException, instance.evolve_model, end_time = 2*max_age, 
            expected_message = "Error when calling 'evolve_for' of a 'EVtwin', errorcode "
                "is 5, error is 'PRINTB -- age greater than limit'")

        instance.stop()

        
    def xtest5(self):
        print "Testing adding and removing particles from stellar evolution code..."
        
        particles = Particles(3)
        particles.mass = 1.0 | units.MSun
        
        instance = EVtwin()
        instance.initialize_code()
        instance.commit_parameters()
        stars = instance.particles
        self.assertEquals(len(stars), 0) # before creation
        stars.add_particles(particles[:-1])
        instance.commit_particles()
        instance.evolve_model(1.0 | units.Myr)
        self.assertEquals(len(stars), 2) # before remove
        self.assertAlmostEqual(stars.age, 1.0 | units.Myr)
        
        stars.remove_particle(particles[0])
        self.assertEquals(len(stars), 1)
        self.assertEquals(instance.get_number_of_particles(), 1)
        instance.evolve_model(2.0 | units.Myr)
        self.assertAlmostEqual(stars[0].age, 2.0 | units.Myr)
        
        stars.add_particles(particles[::2])
        self.assertEquals(len(stars), 3) # it's back...
        self.assertAlmostEqual(stars[0].age, 2.0 | units.Myr)
        self.assertAlmostEqual(stars[1].age, 0.0 | units.Myr)
        self.assertAlmostEqual(stars[2].age, 0.0 | units.Myr) # ... and rejuvenated.
        
        instance.evolve_model(3.0 | units.Myr) # The young stars keep their age offset from the old star
        self.assertAlmostEqual(stars.age, [3.0, 1.0, 1.0] | units.Myr)
        instance.evolve_model(4.0 | units.Myr)
        self.assertAlmostEqual(stars.age, [4.0, 2.0, 2.0] | units.Myr)
        instance.stop()

    def xtest6(self):
        print "Test for obtaining the stellar structure model"
        stars = Particles(2)
        stars.mass = [1.0, 10.0] | units.MSun
        instance = EVtwin()
        instance.initialize_code()
        instance.commit_parameters()
        instance.particles.add_particles(stars)
        instance.commit_particles()
        instance.evolve_model()
        self.assertEquals(instance.particles.get_number_of_zones(), [199, 199])
        self.assertEquals(len(instance.particles[0].get_radius_profile()), 199)
        self.assertRaises(AmuseException, instance.particles.get_radius_profile, 
            expected_message = "Querying radius profiles of more than one particle at a time is not supported.")
        self.assertEquals(len(instance.particles[1].get_density_profile()), 199)
        self.assertIsOfOrder(instance.particles[0].get_radius_profile()[-1],          1.0 | units.RSun)
        self.assertIsOfOrder(instance.particles[0].get_temperature_profile()[0],  1.0e7 | units.K)
        self.assertIsOfOrder(instance.particles[0].get_temperature_profile()[-1],  5.0e3 | units.K)
        radius1 = instance.particles[0].get_radius_profile()
        radius2 = radius1[:-1]
        radius2.prepend(0|units.m)
        delta_radius_cubed = (radius1**3 - radius2**3)
        total_mass = (4./3. * pi * instance.particles[0].get_density_profile() * delta_radius_cubed).sum()
        self.assertAlmostRelativeEqual(total_mass, stars[0].mass, places = 1)
        self.assertAlmostEquals(instance.particles[0].get_mu_profile(), [0.62]*199 | units.amu, places=1)
        instance.stop()
        del instance
    
    def xtest7(self):
        print "Test for obtaining the stellar composition structure"
        stars = Particles(1)
        stars.mass = 1.0 | units.MSun
        instance = EVtwin()
        instance.initialize_code()
        instance.commit_parameters()
        instance.particles.add_particles(stars)
        instance.commit_particles()
        instance.evolve_model()
        instance.evolve_model()
        number_of_zones   = instance.particles.get_number_of_zones()[0]
        number_of_species = instance.particles.get_number_of_species()[0]
        composition       = instance.particles[0].get_chemical_abundance_profiles()
        species_names     = instance.particles[0].get_names_of_species()
        self.assertEquals(number_of_zones,    199)
        self.assertEquals(number_of_species,    9)
        self.assertEquals(len(species_names),  number_of_species)
        self.assertEquals(len(composition),    number_of_species)
        self.assertEquals(len(composition[0]), number_of_zones)
        self.assertEquals(species_names, ['h1', 'he4', 'c12', 'n14', 'o16', 'ne20', 'mg24', 'si28', 'fe56'])
        self.assertAlmostEquals(composition[0, -1],        0.7, 4)
        self.assertAlmostEquals(composition[1, -1],        0.3 - instance.parameters.metallicity, 4)
        self.assertAlmostEquals(composition[2:,-1].sum(),  instance.parameters.metallicity, 4)
        self.assertAlmostEquals(composition.sum(axis=0), [1.0]*number_of_zones)
        instance.stop()
        del instance
    
    def slowtest8(self):
        print "Test for obtaining the stellar composition structure - evolved star"
        stars = Particles(1)
        stars.mass = 1.0 | units.MSun
        instance = EVtwin()
        instance.initialize_code()
        instance.commit_parameters()
        instance.particles.add_particles(stars)
        instance.commit_particles()
        instance.evolve_model(11.7 | units.Gyr)
        self.assertTrue(instance.particles[0].age >= 11.7 | units.Gyr)
        self.assertTrue(str(instance.particles[0].stellar_type) == "First Giant Branch")
        number_of_zones   = instance.particles.get_number_of_zones()[0]
        number_of_species = instance.particles.get_number_of_species()[0]
        composition       = instance.particles[0].get_chemical_abundance_profiles()
        species_names     = instance.particles[0].get_names_of_species()
        self.assertEquals(number_of_zones,    199)
        self.assertEquals(number_of_species,    9)
        self.assertEquals(len(species_names),  number_of_species)
        self.assertEquals(len(composition),    number_of_species)
        self.assertEquals(len(composition[0]), number_of_zones)
        self.assertEquals(species_names, ['h1', 'he4', 'c12', 'n14', 'o16', 'ne20', 'mg24', 'si28', 'fe56'])
        self.assertAlmostRelativeEquals(composition[0, -1],        0.7 | units.none, 1)
        self.assertAlmostRelativeEquals(composition[1, -1],        0.3 - instance.parameters.metallicity, 1)
        self.assertAlmostRelativeEquals(composition[2:,-1].sum(),  instance.parameters.metallicity, 1)
        self.assertAlmostEquals(composition.sum(axis=0), [1.0]*number_of_zones | units.none)
        self.assertAlmostEquals(composition[0, 0],        0.00 | units.none)
        self.assertAlmostEquals(composition[1, 0],        1.00 - instance.parameters.metallicity, 3)
        self.assertAlmostEquals(composition[2:,0].sum(),  instance.parameters.metallicity, 3)
        instance.stop()
        del instance
    
    def xtest9(self):
        print "Test for changing the stellar structure model (not yet implemented)"
        star = Particles(1)
        star.mass = 1.0 | units.MSun
        instance = EVtwin()
        instance.initialize_code()
        instance.commit_parameters() 
        instance.particles.add_particles(star)
        instance.commit_particles()
        instance.evolve_model()

        density_profile = instance.particles[0].get_density_profile()
        
        self.assertRaises(AmuseException, instance.particles[0].set_density_profile, density_profile[2:], 
            expected_message = "The length of the supplied vector (197) does not match the number of "
            "mesh zones of the star (199).")
        
        mass_factor = 1.1
        instance.particles[0].set_density_profile(mass_factor*density_profile)
        self.assertAlmostRelativeEqual(instance.particles[0].get_density_profile(), density_profile*mass_factor, places=10)
        instance.particles.mass *= mass_factor
        instance.evolve_model()
        
        outer_radius = instance.particles[0].get_radius_profile()
        inner_radius = outer_radius[:-1]
        inner_radius.prepend(0|units.m)
        delta_radius_cubed = (outer_radius**3 - inner_radius**3)
        integrated_mass = (4./3.*pi*delta_radius_cubed*instance.particles[0].get_density_profile()).sum()
        self.assertAlmostRelativeEqual(integrated_mass, star.mass*mass_factor, places = 3)
        instance.stop()
        del instance
    
    def xtest10(self):
        print "Test for changing the stellar composition (not yet implemented)"
        star = Particles(1)
        star.mass = 1.0 | units.MSun
        instance = EVtwin()
        instance.initialize_code()
        instance.commit_parameters()
        instance.particles.add_particles(star)
        instance.commit_particles()
        instance.evolve_model()
        
        composition       = instance.particles[0].get_chemical_abundance_profiles()
        h1_profile = composition[0] * 1
        he4_profile = composition[1] * 1
        k_surface = -1 # index to the outer mesh cell (surface)
        
        self.assertAlmostEquals(composition[0, k_surface],  0.7 | units.none, 4)
        self.assertAlmostEquals(composition[1, k_surface],  (0.3 | units.none) - instance.parameters.metallicity, 4)
        self.assertAlmostEquals(composition[2: , k_surface].sum(),  instance.parameters.metallicity, 4)
        
        composition[0] = he4_profile
        composition[1] = h1_profile
        instance.particles[0].set_chemical_abundance_profiles(composition)
        instance.evolve_model()
        
        composition       = instance.particles[0].get_chemical_abundance_profiles()
        self.assertAlmostEquals(composition[0, k_surface],  (0.3 | units.none) - instance.parameters.metallicity, 4)
        self.assertAlmostEquals(composition[1, k_surface],  0.7 | units.none, 4)
        self.assertAlmostEquals(composition[2: , k_surface].sum(),  instance.parameters.metallicity, 4)
        self.assertAlmostEquals(composition.sum(axis=0), 1.0 | units.none)
        
        self.assertRaises(AmuseException, instance.particles[0].set_chemical_abundance_profiles, composition[:7], 
            expected_message = "The length of the supplied vector (7) does not match the number of "
            "chemical species of the star (8).")
        instance.stop()
        del instance
    
    def slowtest11(self):
        print "Test 11: Continue the stellar evolution of a 'merger product' - WIP"
        instance = EVtwin()
        instance.initialize_code()
        instance.commit_parameters()
        
        instance.parameters.min_timestep_stop_condition = 1.0 | units.s
        
        stars = Particles(3)
        stars.mass = [1.0, 2.0, 1.0] | units.MSun
        instance.particles.add_particles(stars)
        instance.commit_particles()
        instance.evolve_model(1.0 | units.Myr)
        stellar_models = instance.native_stars.internal_structure()
        
        self.assertEqual(len(stellar_models), 3)
        self.assertEqual(len(stellar_models[0]), 199)
        self.assertEqual(len(stellar_models[1]), 199)
        self.assertAlmostEqual(stellar_models[0].mass[198], 1.0 | units.MSun, 2)
        self.assertAlmostEqual(stellar_models[1].mass[198], 2.0 | units.MSun, 2)
        self.assertAlmostEqual(stellar_models[0].mass[0], 0.0 | units.MSun, 2)
        
        instance.new_particle_from_model(stellar_models[0], instance.particles[0].age)
        self.assertEqual(len(instance.particles), 4)
        self.assertEqual(len(instance.imported_stars), 1)
        imported_stellar_model = instance.imported_stars[0].internal_structure()
        self.assertEqual(len(imported_stellar_model), 199)
        self.assertAlmostEqual(imported_stellar_model.mass[198], 1.0 | units.MSun, 2)
        self.assertAlmostEqual(imported_stellar_model.mass[0], 0.0 | units.MSun, 2)
        self.assertAlmostRelativeEqual(imported_stellar_model.X_H, stellar_models[0].X_H, 5)
        self.assertAlmostRelativeEqual(imported_stellar_model.X_He, stellar_models[0].X_He, 5)
        self.assertAlmostRelativeEqual(imported_stellar_model.mass, stellar_models[0].mass, 2)
        self.assertAlmostRelativeEqual(imported_stellar_model.radius[1:], stellar_models[0].radius[1:], 2)
#        instance.evolve_model(2.0 | units.Myr)
        print instance.particles
        instance.stop()
        del instance
    
    def xtest12a(self):
        print "Testing basic operations: evolve_one_step and evolve_for"
        stars = Particles(2)
        stars.mass = 1.0 | units.MSun
        instance = EVtwin()
        se_stars = instance.particles.add_particles(stars)
        self.assertAlmostEqual(se_stars.age, [0.0, 0.0] | units.yr)
        
        for i in range(3):
            se_stars[0].evolve_one_step()
        self.assertAlmostEqual(se_stars.age, [225488.337629, 0.0] | units.yr, 3)
        number_of_steps = 10
        step_size = se_stars[0].age / number_of_steps
        for i in range(1, number_of_steps + 1):
            se_stars[1].evolve_for(step_size)
            self.assertAlmostEqual(se_stars.age, [number_of_steps, i] * step_size)
        print se_stars
        self.assertAlmostRelativeEqual(se_stars[0].age,         se_stars[1].age)
        self.assertAlmostRelativeEqual(se_stars[0].luminosity,  se_stars[1].luminosity, 3)
        self.assertAlmostRelativeEqual(se_stars[0].radius,      se_stars[1].radius, 3)
        self.assertAlmostRelativeEqual(se_stars[0].temperature, se_stars[1].temperature, 3)
        instance.stop()
    
    def xtest12b(self):
        print "Testing basic operations: evolve_one_step and evolve_for (on subset, WIP: Ticket 304)"
        stars = Particles(2)
        stars.mass = 1.0 | units.MSun
        instance = EVtwin()
        se_stars = instance.particles.add_particles(stars)
        self.assertAlmostEqual(se_stars.age, [0.0, 0.0] | units.yr)
        
        for i in range(3):
            se_stars[0].evolve_one_step()
        self.assertAlmostEqual(se_stars.age, [225488.337629, 0.0] | units.yr, 3)
        number_of_steps = 10
        step_size = se_stars[0].age / number_of_steps
        for i in range(1, number_of_steps + 1):
            se_stars[1:].evolve_for(step_size)
            self.assertAlmostEqual(se_stars.age, [number_of_steps, i] * step_size)
        print se_stars
        self.assertAlmostRelativeEqual(se_stars[0].age,         se_stars[1].age)
        self.assertAlmostRelativeEqual(se_stars[0].luminosity,  se_stars[1].luminosity, 3)
        self.assertAlmostRelativeEqual(se_stars[0].radius,      se_stars[1].radius, 3)
        self.assertAlmostRelativeEqual(se_stars[0].temperature, se_stars[1].temperature, 3)
        instance.stop()
    
    def xtest13(self):
        print "Test evolve_model optional arguments: end_time and keep_synchronous"
        stars = Particles(3)
        stars.mass = [1.0, 2.0, 3.0] | units.MSun
        instance = EVtwin()
        instance.particles.add_particles(stars)
        
        self.assertAlmostEqual(instance.particles.age, [0.0, 0.0, 0.0] | units.yr)
        self.assertAlmostEqual(instance.particles.time_step, [70465.105509, 6063.68785133, 1876.53255132] | units.yr, 3)
        
        print "evolve_model without arguments: use shared timestep = 0.99*min(particles.time_step)"
        instance.evolve_model()
        self.assertAlmostEqual(instance.particles.age, 0.99*([1876.53255132,1876.53255132,1876.53255132] | units.yr), 3)
        self.assertAlmostEqual(instance.particles.time_step, [70465.105509,6063.68785133,1876.53255132] | units.yr, 3)
        self.assertAlmostEqual(instance.model_time, 0.99*1876.53255132 | units.yr, 3)
        
        print "evolve_model with end_time: take timesteps, until end_time is reached exactly"
        instance.evolve_model(15000 | units.yr)
        self.assertAlmostEqual(instance.particles.age, [15000.0, 15000.0, 15000.0] | units.yr, 3)
        self.assertAlmostEqual(instance.particles.time_step, [ 84558.1266108,7276.4254216,2251.83906159] | units.yr, 3)
        self.assertAlmostEqual(instance.model_time, 15000.0 | units.yr, 3)
        
        print "evolve_model with keep_synchronous: use non-shared timestep, particle ages will typically diverge"
        instance.evolve_model(keep_synchronous = False)
        self.assertAlmostEqual(instance.particles.age, (15000 | units.yr) + ([ 84558.1266108,7276.4254216,2251.83906159] | units.yr), 3)
        self.assertAlmostRelativeEquals(instance.particles.time_step, [101469.751933,8731.71050591,2702.2068739] | units.yr, 1)
        self.assertAlmostEqual(instance.model_time, 15000.0 | units.yr, 3) # Unchanged!
        instance.stop()
    
    def xtest14(self):
        print "Testing EVtwin states"
        stars = Particles(2)
        stars.mass = 1.0 | units.MSun
        instance = EVtwin()
        
        print "First do everything manually:",
        self.assertEquals(instance.get_name_of_current_state(), 'UNINITIALIZED')
        instance.initialize_code()
        self.assertEquals(instance.get_name_of_current_state(), 'INITIALIZED')
        instance.commit_parameters()
        self.assertEquals(instance.get_name_of_current_state(), 'EDIT')
        instance.particles.add_particle(stars[0])
        instance.commit_particles()
        self.assertEquals(instance.get_name_of_current_state(), 'RUN')
        instance.cleanup_code()
        self.assertEquals(instance.get_name_of_current_state(), 'END')
        instance.stop()
        print "ok"

        print "initialize_code(), commit_parameters(), (re)commit_particles(), " \
            "and cleanup_code() should be called automatically:",
        instance = EVtwin()
        self.assertEquals(instance.get_name_of_current_state(), 'UNINITIALIZED')
        instance.parameters.RGB_wind_setting = -0.5
        self.assertEquals(instance.get_name_of_current_state(), 'INITIALIZED')
        instance.particles.add_particle(stars[0])
        self.assertEquals(instance.get_name_of_current_state(), 'EDIT')
        mass = instance.particles[0].mass
        self.assertEquals(instance.get_name_of_current_state(), 'RUN')
        instance.particles.add_particle(stars[1])
        self.assertEquals(instance.get_name_of_current_state(), 'UPDATE')
        mass = instance.particles[0].mass
        self.assertEquals(instance.get_name_of_current_state(), 'RUN')
        instance.stop()
        self.assertEquals(instance.get_name_of_current_state(), 'STOPPED')
        print "ok"

    def slowtest15(self):
        print "test evolution of 1000 star sampled over flattish IMF"
        
        number_of_stars=1000
        
        from amuse.ic.salpeter import new_salpeter_mass_distribution
        import numpy

        class notsorandom(object):
            def random(self,N):
                return numpy.array(range(N))/(N-1.)

        masses = new_salpeter_mass_distribution(
            number_of_stars, 
            mass_min = 0.1 | units.MSun,
            mass_max = 100.0 | units.MSun, 
            alpha = -1.01,random=notsorandom()
        )
 
        stars = Particles(mass=masses)

        instance=EVtwin()
        instance.parameters.maximum_number_of_stars=number_of_stars
        instance.parameters.min_timestep_stop_condition=.001 | units.s
        instance.particles.add_particles(stars)
        
        i=0
        for p in instance.particles:
          print i,p.mass
          p.evolve_for(0.1 | units.Myr)
          i+=1

    def xslowtest16(self):
        print "test full evolution of 1000 star sampled over flattish IMF"
        
        number_of_stars=1000
        
        from amuse.ic.salpeter import new_salpeter_mass_distribution
        import numpy

        class notsorandom(object):
            def random(self,N):
                return numpy.array(range(N))/(N-1.)

        masses = new_salpeter_mass_distribution(
            number_of_stars, 
            mass_min = 0.1 | units.MSun,
            mass_max = 100.0 | units.MSun, 
            alpha = -1.01,random=notsorandom()
        )
 
        stars = Particles(mass=masses)

        instance=EVtwin()
        instance.parameters.maximum_number_of_stars=number_of_stars
        instance.particles.add_particles(stars)
        
        for p in instance.particles:
          p.evolve_for(13.2 | units.Gyr)

    def slowtest17(self):
        """
        We add multiple particles to evtwin and evolve the stars
        individualy. Evtwin crashes on some combinaties of 
        star masses and which star is evolved first.
        """
        exceptions = []
        for i, (masses, indices) in  enumerate([
                (
                    [1.21372730283, 1.22207032494, 11.21372730283] | units.MSun,
                    (0,1)
                ),
                (
                    [1.21372730283, 1.22207032494, 1.21372730283] | units.MSun,
                    (0,1)
                ),
                ( 
                    [1.21372730283, 1.22207032494, 1.21372730283] | units.MSun,
                    (1,0)
                ),
                (
                    [1.21372730283, 1.22207032494] | units.MSun,
                    (0,1)
                ),
                (
                    [1.21372730283, 11.22207032494, 1.21372730283] | units.MSun,
                    (0,1)
                ),
                (
                    [1.21372730283, 1.21372730283, 1.21372730283] | units.MSun,
                    (0,1)
                ),
                (
                    [1.21372730283, 1.22207032494, 1.21372730283] | units.MSun,
                    (0,1)
                ),
                (
                    [0.101, 1.22207032494, 1.21372730283] | units.MSun,
                    (0,1)
                )
            ]):
            
            stars = Particles(mass=masses)

            instance=EVtwin()
            instance.particles.add_particles(stars)
            
            try:
                index_in_indices = 0
                instance.particles[indices[index_in_indices]].evolve_for(0.1| units.Myr)
                index_in_indices = 1
                instance.particles[indices[index_in_indices]].evolve_for(0.1| units.Myr)
            except AmuseException as ex:
                exceptions.append( [i, masses, indices, index_in_indices] )
            
            instance.stop()
            
        if len(exceptions) > 0:
            failure_message = ''
            for index, masses, indices, index_in_indices in exceptions:
                failure_message += '[{0}]: error in '.format(index)
                failure_message += 'first' if index_in_indices == 0 else 'second'
                failure_message += ' evolve_for,'
                failure_message += ' index: {0},'.format(indices[index_in_indices])
                failure_message += ' masses (MSun): {0}.\n'.format(masses.value_in(units.MSun))
            
            self.fail(failure_message)
    
    def xtest18(self):
        print "Testing EVtwin calculate_core_mass"
        instance = EVtwin()#redirection="none")
        star = instance.particles.add_particle(Particle(mass=1|units.MSun))
        instance.evolve_model(0.4|units.Gyr) # VERY short, for test speed up
        central_hydrogen_abundance = star.get_chemical_abundance_profiles()[0][0]
        self.assertTrue(central_hydrogen_abundance < 0.68) # some hydrogen is burned
        self.assertTrue(central_hydrogen_abundance > 0.67) # ... but not that much yet
        self.assertEqual(star.calculate_core_mass(core_H_abundance_limit=0.67), 0 | units.MSun)
        self.assertAlmostEqual(star.calculate_core_mass(core_H_abundance_limit=0.71), 1 | units.MSun, 1)
        
        # For test speed up, we use a weird core_H_abundance_limit to define the "hydrogen exhausted core"
        limit = 0.68
        expected_core_mass = 0.0123182798542 | units.MSun
        self.assertAlmostEqual(star.calculate_core_mass(core_H_abundance_limit=limit), expected_core_mass, 3)
        
        species_names = star.get_names_of_species()
        self.assertEquals(species_names, ['h1', 'he4', 'c12', 'n14', 'o16', 'ne20', 'mg24', 'si28', 'fe56'])
        h1_core_mass = star.calculate_core_mass(species=["h1"], core_H_abundance_limit=limit)
        he4_core_mass = star.calculate_core_mass(species=["he4"], core_H_abundance_limit=limit)
        c12_core_mass = star.calculate_core_mass(species=["c12"], core_H_abundance_limit=limit)
        n14_core_mass = star.calculate_core_mass(species=["n14"], core_H_abundance_limit=limit)
        o16_core_mass = star.calculate_core_mass(species=["o16"], core_H_abundance_limit=limit)
        ne20_core_mass = star.calculate_core_mass(species=["ne20"], core_H_abundance_limit=limit)
        mg24_core_mass = star.calculate_core_mass(species=["mg24"], core_H_abundance_limit=limit)
        si28_core_mass = star.calculate_core_mass(species=["si28"], core_H_abundance_limit=limit)
        fe56_core_mass = star.calculate_core_mass(species=["fe56"], core_H_abundance_limit=limit)
        metal_core_mass = star.calculate_core_mass(species=["c12", "n14", "o16", "ne20", "mg24", "si28", "fe56"], core_H_abundance_limit=limit)
        instance.stop()
        self.assertAlmostRelativeEqual(h1_core_mass, expected_core_mass*0.68, 2)
        self.assertAlmostRelativeEqual(he4_core_mass, expected_core_mass*0.30, 2)
        self.assertAlmostRelativeEqual(metal_core_mass, expected_core_mass*0.02, 1)
        self.assertAlmostRelativeEqual(expected_core_mass, he4_core_mass + metal_core_mass + h1_core_mass, 7)
        self.assertAlmostRelativeEqual(metal_core_mass, c12_core_mass + n14_core_mass +
            o16_core_mass + ne20_core_mass + mg24_core_mass + si28_core_mass + fe56_core_mass, 7)
    
    def xtest19(self):
        print "Testing EVtwin central_temperature and central_density"
        instance = EVtwin()
        stars = instance.particles.add_particles(Particles(mass=[0.1, 1, 10]|units.MSun))
        self.assertIsOfOrder(stars.central_temperature, [4e6, 13e6, 31e6] | units.K)
        self.assertIsOfOrder(stars.central_density, [400, 77, 9] | units.g * units.cm**-3)
        instance.stop()
    

