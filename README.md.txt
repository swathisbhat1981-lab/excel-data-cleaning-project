# Excel Data Cleaning Pipeline

A Python-based data cleaning project using Pandas and NumPy to clean, validate, and standardize an Excel dataset.

## Project Overview

This project demonstrates a simple data-cleaning pipeline for an Excel dataset containing 1,200 rows and 14 columns.

The pipeline performs:

- Missing value handling
- Duplicate detection
- Order ID validation
- Tracking number validation
- Date standardization
- Text formatting checks
- Numeric precision enforcement
- Final data-quality validation

## Data Cleaning Steps

### 1. Missing Values

Missing CouponCode values were replaced with:

`No Coupon`

This was treated as a meaningful category rather than using mean, median, or mode imputation.

### 2. Duplicate Detection

The dataset was checked for:

- Full-row duplicates
- Duplicate Order IDs
- Duplicate Tracking Numbers

No duplicates were found.

### 3. Date Standardization

Dates were converted into ISO 8601 format:

`YYYY-MM-DD`

### 4. Numeric Formatting

UnitPrice and TotalPrice values were standardized to two decimal places.

### 5. Validation

The final dataset passed the validation checks:

- Duplicate Orders: 0
- Incorrectly formatted dates: 0

## Technologies Used

- Python
- Pandas
- NumPy
- OpenPyXL

## How to Run

Install the required libraries:

```bash
pip install -r requirements.txt