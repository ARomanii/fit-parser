from fastapi import FastAPI, UploadFile, File, HTTPException
import fitparse
import io

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "FIT Parser is running!"}

@app.post("/parse-fit")
async def parse_fit(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        fitfile = fitparse.FitFile(io.BytesIO(contents))
        
        records = []
        laps = []
        
        # Читаємо посекундні дані (Records)
        for record in fitfile.get_messages('record'):
            data = record.get_values()
            records.append({
                'timestamp': str(data.get('timestamp')),
                'heart_rate': data.get('heart_rate'),
                'speed': data.get('enhanced_speed') or data.get('speed'),
                'cadence': data.get('cadence'),
                'distance': data.get('distance')
            })
            
        # Читаємо відрізки/кола (Laps / Splits)
        for lap in fitfile.get_messages('lap'):
            data = lap.get_values()
            laps.append({
                'start_time': str(data.get('start_time')),
                'total_elapsed_time': data.get('total_elapsed_time'),
                'total_distance': data.get('total_distance'),
                'avg_heart_rate': data.get('avg_heart_rate'),
                'max_heart_rate': data.get('max_heart_rate'),
                'avg_speed': data.get('enhanced_avg_speed') or data.get('avg_speed')
            })

        return {
            "success": True,
            "filename": file.filename,
            "total_records": len(records),
            "laps_count": len(laps),
            "laps": laps,
            "sample_records": records[:10]
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing FIT file: {str(e)}")
