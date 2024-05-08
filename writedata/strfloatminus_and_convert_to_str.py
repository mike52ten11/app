
import decimal


def strfloatminus_and_convert_to_str(strfloat1,strfloat2):
     
    if (decimal.Decimal(strfloat2)-decimal.Decimal(strfloat1))<0 :

        return str(decimal.Decimal(strfloat1)-decimal.Decimal(strfloat2))

    else: 
    
        return str(decimal.Decimal(strfloat2)-decimal.Decimal(strfloat1))

    





