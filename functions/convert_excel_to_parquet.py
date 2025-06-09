def convert_excel_to_parquet(file_path):
    import duckdb
    
    con = duckdb.connect()
    con.execute("INSTALL excel")
    con.execute("LOAD excel")
    
    con.execute(f"""
    COPY (
        SELECT * FROM read_xlsx('{file_path}', all_varchar=true)
    ) TO '{file_path}.parquet' (FORMAT 'parquet')
        """)
    return f"{file_path}.parquet created successfully"