import logging

def get_execution_context(**context):
    """Get execution date context"""
    execution_date = context['execution_date']
    year = execution_date.year
    month = execution_date.month
    
    logging.info(f"Processing data for: {year}-{month:02d}")
    
    return {
        'year': year,
        'month': month,
        'year_month': f"{year}{month:02d}",
        'execution_date': execution_date
    }
