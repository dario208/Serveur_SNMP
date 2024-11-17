from fastapi import FastAPI, HTTPException
from pysnmp.hlapi import (CommunityData, ContextData, ObjectIdentity,
                          ObjectType, SnmpEngine, UdpTransportTarget, getCmd)

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Welcome to the SNMP-FastAPI server!"}

def snmp_get(host, oid, community="public", port=161):
    """
    Function to perform SNMP GET request.
    :param host: SNMP device IP or hostname.
    :param oid: SNMP Object Identifier (OID) to query.
    :param community: SNMP community string (default: "public").
    :param port: SNMP port (default: 161).
    :return: SNMP response value.
    """
    try:
        iterator = getCmd(
            SnmpEngine(),
            CommunityData(community),
            UdpTransportTarget((host, port)),
            ContextData(),
            ObjectType(ObjectIdentity(oid))
        )

        error_indication, error_status, error_index, var_binds = next(iterator)

        if error_indication:
            raise Exception(error_indication)
        elif error_status:
            raise Exception(f"{error_status.prettyPrint()} at {error_index and var_binds[int(error_index) - 1][0] or '?'}")
        else:
            for var_bind in var_binds:
                return var_bind[1].prettyPrint()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/snmp/{oid}")
async def get_snmp_data(oid: str, host: str, community: str = "public", port: int = 161):
    """
    FastAPI route to get SNMP data.
    :param oid: SNMP OID to query.
    :param host: SNMP device IP or hostname.
    :param community: SNMP community string (default: "public").
    :param port: SNMP port (default: 161).
    :return: SNMP response value.
    """
    value = snmp_get(host, oid, community, port)
    return {"oid": oid, "value": value}
