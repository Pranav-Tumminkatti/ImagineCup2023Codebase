function validate(){
    let starttrue = document.forms["part2"]["starttime"].value;
    if (starttrue=='true'){
        let starttime_h = document.forms["part2"]["starttime_h"].value;
        let starttime_m = document.forms["part2"]["starttime_m"].value;
        let endtime_h = document.forms["part2"]["endtime_h"].value;
        let endtime_m = document.forms["part2"]["endtime_m"].value;
        if ((starttime_h == endtime_h)){
            if(starttime_m < endtime_m){
                return true;
            }
            else{
                alert('Start time cannot be after end time')
                return false;
            }
        }
        else if (starttime_h < endtime_h){
            return true;
        }
        else{
            alert('Start time cannot be after end time')
            return false;
        }
    }
    else{
        return true;
    }
}