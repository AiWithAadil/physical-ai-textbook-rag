---
sidebar_position: 2
title: Tools and Setup
description: Setting up your Physical AI development environment
---

# Tools and Setup

## Development Environment

### Python Installation

**Required**: Python 3.11 or later

```bash
# Check Python version
python --version

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip
```

### Essential Python Libraries

```bash
# Core scientific computing
pip install numpy scipy matplotlib

# Robotics and simulation
pip install pybullet  # PyBullet physics engine
pip install opencv-python  # Computer vision

# Machine learning
pip install scikit-learn tensorflow pytorch

# Testing
pip install pytest

# Jupyter for interactive development
pip install jupyter notebook
```

## Recommended Tools

### Text Editors / IDEs

- **VS Code**: Lightweight, extensive Python support
- **PyCharm**: Full-featured Python IDE
- **Jupyter Notebook**: Interactive development and visualization

### Version Control

```bash
# Install Git
# https://git-scm.com/

# Configure Git
git config --global user.name "Your Name"
git config --global user.email "your@email.com"

# Clone Physical AI textbook
git clone https://github.com/physical-ai/physical-ai-book.git
cd physical-ai-book
```

### Simulation Frameworks

#### PyBullet

```bash
pip install pybullet
```

**Resources**:
- [PyBullet Documentation](https://pybullet.org/)
- Quick start: Simple simulation of a falling sphere

#### Gazebo

Cross-platform simulator with ROS integration

**Installation**: https://gazebosim.org/

### ROS (Robot Operating System)

Middleware for robotics projects (optional but useful)

**Installation**: https://www.ros.org/

## Hardware (Optional)

For hands-on experiments with real robots:

### Beginner Kits
- LEGO Mindstorms
- VEX Robotics
- Arduino + sensor kits

### Advanced Systems
- TurtleBot3
- ABB IRB robots
- Franka Emika Panda

## Running Code Examples

### Basic Python Script

```bash
cd examples/chapter-01
python sensor_simulation.py
```

### Running Tests

```bash
# From project root
pytest tests/code-validation/

# Run specific test
pytest tests/code-validation/test_chapter_01.py
```

### Interactive Exploration

```bash
# Start Jupyter notebook
jupyter notebook

# Navigate to examples/notebooks/
```

## Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'pybullet'`
- **Solution**: `pip install pybullet`

**Issue**: Python 3.11 not found
- **Solution**: Download from https://www.python.org/ and install

**Issue**: Virtual environment not activating
- **Solution**: Try `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)

## Resources for Learning

### Official Documentation
- [Python docs](https://docs.python.org/3/)
- [NumPy docs](https://numpy.org/)
- [PyBullet docs](https://pybullet.org/)
- [OpenCV docs](https://docs.opencv.org/)

### Tutorials
- Python basics: https://docs.python.org/3/tutorial/
- NumPy quickstart: https://numpy.org/doc/stable/user/basics.html
- OpenCV tutorials: https://docs.opencv.org/master/d9/df8/tutorial_root.html

### Community Resources
- Stack Overflow: Search existing questions
- GitHub Issues: Report bugs or ask questions
- Reddit: r/robotics, r/MachineLearning

## Next Steps

1. **Install Python 3.11+**
2. **Create a virtual environment**
3. **Install required libraries**
4. **Clone the textbook repository**
5. **Run first code example** from Chapter 1

Welcome to Physical AI development!

