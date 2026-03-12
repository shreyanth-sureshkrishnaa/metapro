# metapro: Bulk Metadata Extractor

metapro is a high-performance forensic tool designed for the bulk extraction, analysis, and visualization of digital metadata from image files. It leverages ExifTool for deep metadata parsing and provides a unified interface for temporal and geospatial analysis.

## Core Capabilities

The application processes large datasets to extract technical metadata including camera specifications, encoding details, and embedded GPS coordinates. It includes a dedicated map interface for geospatial distribution analysis and a synchronized timeline for event reconstruction. Data can be exported to CSV format for further investigation in external analytical tools.

## Prerequisites

The application is built using PySide6 and requires a Linux environment with X11 support for GUI rendering. Hardware acceleration via OpenGL is recommended for optimal performance of the map and timeline components.

## Installation

The primary method for deployment is via the provided Docker configuration, which ensures all necessary system libraries for Qt and WebEngine are correctly configured.

### Local Environment Setup

Users preferring a native installation must ensure that ExifTool and the following system dependencies are installed:
- Qt 6 Runtime Libraries
- X11 and XCB plugins
- OpenGL and EGL drivers

Python dependencies can be installed using the requirements file:
pip install -r requirements.txt

## Docker Deployment

The project includes a comprehensive containerization strategy to handle complex graphical dependencies and GPU passthrough.

### Configuration

The provided run script manages X11 socket mapping and GPU device access. 

To build and launch the application:
./run.sh --build

### Data Mounting

To analyze an external dataset, provide the absolute path to the directory containing the media files:
./run.sh /path/to/media/directory

The dataset will be mounted as a read-only volume inside the container at /data, ensuring the integrity of the original evidence.

## Technical Architecture

The system follows a modular component architecture:
- Core Engine: Python and ExifTool for metadata extraction and parsing.
- UI Layer: PySide6 (Qt) for the primary graphical interface.
- Visualization: QWebEngine for map rendering and custom QML/Widget components for timeline visualization.
- Security: Non-root execution and container isolation for forensic workflows.
