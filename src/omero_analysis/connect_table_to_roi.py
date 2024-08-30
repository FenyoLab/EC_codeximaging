from omero.gateway import BlitzGateway
from omero.model import RoiAnnotationLinkI, RoiI, FileAnnotationI
from omero.sys import ParametersI
from getpass import getpass


# Step 1 - Connect/Disconnect
def connect(hostname, username, password):
    """
    Connect to an OMERO server
    :param hostname: Host name
    :param username: User
    :param password: Password
    :return: Connected BlitzGateway
    """
    conn = BlitzGateway(username, password,
                        host=hostname, secure=True)
    conn.connect()
    conn.c.enableKeepAlive(60)
    return conn


def disconnect(conn):
    """
    Disconnect from an OMERO server
    :param conn: The BlitzGateway
    """
    conn.close()

def link_table_to_roi(gateway, table_id, roi_id):
    """
    Link an OMERO.table to a ROI object

    :param gateway: An instance of a BlitzGateway object
    :param table_id: The ID of the OMERO.table
    :param roi_ID: The ID of the ROI to link the table to
    """

    query = (
        "select ann from FileAnnotation ann "
        "join fetch ann.file as f "
        "where f.id=:id"
    )
    params = ParametersI()
    params.addId(table_id)
    gateway.SERVICE_OPTS.setOmeroGroup("-1")
    file_ann = gateway.getQueryService().projection(query, params, gateway.SERVICE_OPTS)[0][0].val ##### ERROR LINE
    
    #THE ERROR IS HERE!!!
    #*** IndexError: list index out of range
    #its because fil_ann is empty, this query is not getting anything 

    link = RoiAnnotationLinkI()
    link.parent = RoiI(roi_id, False)
    link.child = FileAnnotationI(file_ann.id.val, False)
    ctx = {'omero.group': str(file_ann.getDetails().getGroup().getId().val)}
    gateway.getUpdateService().saveObject(link, ctx)
    #LOGGER.info(f"Linked table {table_id} to ROI {roi_id}.")

def main():
    hostname = 'omero.nyumc.org'
    username = 'as18894'
    password = getpass("Password: ")
    conn = connect(hostname, username, password)
    table_id = 1515269
    roi_id = 1227056
    link_table_to_roi(conn, table_id, roi_id)
    disconnect(conn)


if __name__ == "__main__":
    main()
