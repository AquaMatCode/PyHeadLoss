# PyHeadLoss

A small program to calculate major and minor head loss

## Description

This piece of code can be used to calculate headlosses in a network based on pipes and fluids properties.
It's using Darcy-Weisbach equation for major headlosses and 3 models to estimate the friction factor :
- Serghide | 1984
- Fang | 2011 | https://www.sciencedirect.com/science/article/pii/S0029549311000173
- Bellos, Nalbantis, Tsakris | 2018 | https://ascelibrary.org/doi/full/10.1061/%28ASCE%29HY.1943-7900.0001540

## Getting Started

### Dependencies

* Using python math library

### Installing

```
git clone https://github.com/AquaMatCode/pyheadloss
```

### Executing program

* To run the program
```
from PyHeadLoss import PyHeadLoss

#Initialize the class with your network values
c = PyHeadLoss(100, 100, 0.002, 0.5, 1000, 0.001, [7, 4, 8])
c.get_head_loss()
```

## Authors

AquaMatCode

## License

This project is licensed under the Unlicence License - see the LICENSE.md file for details

## Acknowledgments

Inspired by https://pypi.org/project/colebrook/#description
