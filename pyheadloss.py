import math

class pyheadloss:
    """
    With inspiration from https://pypi.org/project/colebrook/#description
    """
    
    def __init__(self, pipe_diameter:float, pipe_length:float, flow_rate:float, pipe_roughness:float, volumetric_mass:float, fluid_dynamic_viscosity:float, k_factors:list=None):
        """
        Class initialization

        Args:
            pipe_diameter (float): The diameter of the pipe - millimeters
            pipe_length (float): The lenght of the pipe - meters
            flow_rate (float): The flow rate in the pipe - m3/s
            pipe_roughness (float): The roughness of the pipe - millimeters
            volumetric_mass (float): The volumetric mass of the fluid - kg/m3
            fluid_dynamic_viscosity (float): The fluid dynamic viscosity - Pa/s
            k_factors (list, optional): Plumbing elements coefficients - units
        """
        
        self.pipe_diameter = pipe_diameter/1000
        self.pipe_length = pipe_length
        self.flow_rate = flow_rate
        self.pipe_roughness = pipe_roughness/1000
        self.volumetric_mass = volumetric_mass
        self.fluid_dynamic_viscosity = fluid_dynamic_viscosity
        self.k_factors = k_factors
        
        self.gravity = 9.80665
    
    def calculate_fluid_velocity(self):
        """
        Flowing speed of the fluid calculous

        Returns:
            float: Flowing speed in m/s
        """
        surface = (math.pi * self.pipe_diameter ** 2) / 4
        v = self.flow_rate/surface
        return v
    
    def calculate_relative_roughness(self):
        """
        Relative roughness of the pipe calculous

        Returns:
            float: Relative roughness of the pipe in standard units
        """
        return self.pipe_roughness/self.pipe_diameter
    
    def calculate_reynolds_number(self, fluid_velocity:float):
        """
        Reynolds number calculous
        https://en.wikipedia.org/wiki/Reynolds_number
        
        Args:
            fluid_velocity (float): The velocity of the fluid in m/s

        Returns:
            float: Reynolds number
        """

        return (self.volumetric_mass * fluid_velocity * self.pipe_diameter) / self.fluid_dynamic_viscosity
    
    def check_reynolds_range(self, reynolds_number:float):
        """
        Verifies if Reynolds number is in the correct range

        Args:
            reynolds_number (float)
        """
        if reynolds_number <= 2500:
            exit("Reynolds number is inferior or equal to 2500, none of the presented models can calculate major headlosses") 

    def calculate_friction_factor_serghides(self, relative_roughness, reynolds_number):
        """
        Friction factor according to the following model
        
        Model: Serghide
        Year: 1984
        Paper: ?
        Suitable Range:
            2500 < Reynolds < 10^8
            0 < Rr < 0.05

        Returns:
            float: Friction factor
        """
        
        A = -2 * math.log10((relative_roughness / 3.7) + (12 / reynolds_number))
        B = -2 * math.log10((relative_roughness / 3.7) + (2.51*A / reynolds_number))
        C = -2 * math.log10((relative_roughness / 3.7) + (2.51*B / reynolds_number))
        
        return (A - (((B - A)**2) / (C - 2*B + A)))**-2
    
    
    def calculate_friction_factor_fang(self, relative_roughness, reynolds_number):
        """
        Friction factor according to the following model
        
        Model: Fang
        Year: 2011
        Paper: https://www.sciencedirect.com/science/article/pii/S0029549311000173
        Suitable Range:
            3000 < Reynolds < 10^8
            0 < Rr < 0.05

        Returns:
            float: Friction factor
        """


        return 1.613 * (math.log(0.234 * relative_roughness ** 1.1007 - 60.525 / reynolds_number**1.1105 + 56.291 / reynolds_number**1.0712))**-2
    
    
    def calculate_friction_factor_bnt(self, relative_roughness:float, reynolds_number:float):
        """
        Friction factor according to the following model
        
        Model: Bellos, Nalbantis, Tsakris
        Year: 2018
        Paper: https://www.sciencedirect.com/science/article/pii/S0029549311000173
        Suitable Range:
            3000 < Reynolds < 10^8

        Args:
            relative_roughness (float)
            reynolds_number (float)

        Returns:
            float: Friction factor
        """

        inv_roughness = 1 / relative_roughness
        param_a = 1 / (1 + (reynolds_number / 2712)**8.4)
        param_b = 1 / (1 + (reynolds_number / (150 * inv_roughness))**1.8)
        exponent_a = 2 * (param_a - 1) * param_b
        exponent_b = 2 * (param_a - 1) * (1 - param_b)
        friction = (64 / reynolds_number)**param_a * (0.75 * math.log(reynolds_number / 5.37))**exponent_a * (0.88 * math.log(6.82 *inv_roughness))**exponent_b


        return friction
    
    
    def calculate_friction_factors(self, relative_roughness:float, reynolds_number:float):
        """
        Agregate the different friction factors in a dictionnary based on reynolds_number

        Args:
            relative_roughness (float)
            reynolds_number (float)

        Returns:
            dict: Friction factors
        """
        ffdict = {}
        
        if reynolds_number > 3000:
            ffdict["1984 - Serghide's model"] = self.calculate_friction_factor_serghides(relative_roughness, reynolds_number)
            ffdict["2011 - Fang's model"] = self.calculate_friction_factor_fang(relative_roughness, reynolds_number)
            ffdict["2018 - BNT's model"] = self.calculate_friction_factor_bnt(relative_roughness, reynolds_number)

            
        elif reynolds_number > 2500:
            ffdict["1984 - Serghide's model"] = self.friction_factor_serghides(relative_roughness, reynolds_number)
            
        return ffdict
    
    
    def calculate_major_headloss(self, friction_factor_dict:dict, fluid_velocity:float):
        """
        Create a major headlosses dictionnary according to friction factors

        Args:
            friction_factor_dict (dict)
            fluid_velocity (float)

        Returns:
            dict: Major headlosses dictionnary
        """
        major_headloss_dict = {}

        for key, value in friction_factor_dict.items():
            major_headloss_dict[key] = value * (self.pipe_length / self.pipe_diameter) * ((fluid_velocity ** 2) / (2 * self.gravity))
            
        return major_headloss_dict
    
    def calculate_average_major_headloss(self, major_headloss_dict):
        """
        Calculate the average major headloss

        Args:
            major_headloss_dict (dict)

        Returns:
            float: Average major headloss
        """
        v_sum = 0
        for key, value in major_headloss_dict.items():
            v_sum = v_sum + value

        return v_sum/3
    
    
    def calculate_minor_headloss(self, fluid_velocity:float):
        """
        Calculous of minor headlosses

        Args:
            fluid_velocity (float)

        Returns:
            float: Minor headlosses
        """
        k_sum = 0
        
        for k_factor in self.k_factors:
            k_sum = k_sum + k_factor
        
        return k_sum, (k_sum * fluid_velocity**2 ) / (2*self.gravity)
    
    def output(self, fluid_velocity, relative_roughness, reynolds_number, friction_factors_dict, major_headloss_dict, average_major_headloss, minor_headloss=None, global_k=None):
        print("\n")
        print(" For the following inital values ".center(100, "-"))
        print(f"Pipe diameter : {self.pipe_diameter} meters")
        print(f"Pipe length : {self.pipe_length} meters")
        print(f"Flow rate : {self.flow_rate} m3/s")
        print(f"Pipe roughness : {self.pipe_roughness} meters")
        print(f"Volumetric mass : {self.volumetric_mass} kg/m3")
        print(f"Fluid dynamic viscosity : {self.pipe_roughness} Pa/s")
        
        print("\n")
        
        print(" The program has calculated ".center(100, "-"))
        print(f"Fluid_velocity : {fluid_velocity} m/s")
        print(f"Relative roughness : {relative_roughness}")
        print(f"Reynolds number : {reynolds_number}")
        
        print("\n")
        
        print("Friction factors".center(100, "~"))
        for key, value in friction_factors_dict.items():
            print(f"{key} : {value}")
            
        print("\n")
        
        print("Major headloss".center(100, "~"))
        for key, value in major_headloss_dict.items():
            print(f"{key} : {round(value,6)} mCE") 
            
        print(f"Average major headloss : {round(average_major_headloss,6)} mCE")
        print("\n")
        
        if global_k:
            print("Minor headloss".center(100, "~"))
            print(f"Global k factor : {global_k}")
            print(f"Minor headloss : {round(minor_headloss, 6)} mCE")
            print("\n")
            
            print("Total headloss".center(100, "~"))
            print(f"The sum of average major headloss and minor headloss")
            print(f"{round(minor_headloss+average_major_headloss, 6)} mCE")
        
    def get_headloss(self):
        """
        The main function to calculate headloss based on arguments passed to the class
        """
        fluid_velocity = self.calculate_fluid_velocity()
        reynolds_number = self.calculate_reynolds_number(fluid_velocity)
        self.check_reynolds_range(reynolds_number)

        relative_roughness = self.calculate_relative_roughness()
        friction_factors_dict = self.calculate_friction_factors(relative_roughness, reynolds_number)
        major_headloss_dict = self.calculate_major_headloss(friction_factors_dict, fluid_velocity)
        average_major_headloss = self.calculate_average_major_headloss(major_headloss_dict)
        
        if self.k_factors:
            print("OK")
            global_k, minor_headloss = self.calculate_minor_headloss(fluid_velocity)
        else:
            global_k = None
            minor_headloss = None
            
        self.output(fluid_velocity, relative_roughness, reynolds_number, friction_factors_dict, major_headloss_dict, average_major_headloss, minor_headloss, global_k)


