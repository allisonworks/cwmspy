# -*- coding: utf-8 -*-


from cx_Oracle import DatabaseError


class CwmsLocMixin:
    def store_location(
        self,
        p_location_id,
        p_location_type=None,
        p_elevation=None,
        p_elev_unit_id=None,
        p_vertical_datum=None,
        p_latitude=None,
        p_longitude=None,
        p_horizontal_datum=None,
        p_public_name=None,
        p_long_name=None,
        p_description=None,
        p_time_zone_id=None,
        p_country_name=None,
        p_state_initial=None,
        p_active=None,
        p_ignorenulls="T",
        p_db_office_id=None,
    ):
        """Short summary.

        Parameters
        ----------

        p_location_id : str
            The location identifier.
        p_location_type : str
            A user-defined type for the location.
        p_elevation : float
            The elevation of the location.
        p_elev_unit_id : str
            The elevation unit.
        p_vertical_datum : str
            The datum of the elevation.
        p_latitude : float
            The actual latitude of the location.
        p_longitude : float
            The actual longitude of the location.
        p_horizontal_datum : str
            The datum for the latitude and longitude.
        p_public_name : str
            The public name for the location.
        p_long_name : str
            The long name for the location.
        p_description : str
            A description of the location.
        p_time_zone_id : str
            The time zone name for the location.
        p_country_name : str
            The name of the county that the location is in.
        p_state_initial : str
            The two letter abbreviation of the state that the location is in.
        p_active : str
             flag ('T' or 'F') that specifies whether the location is marked 
             as active.
        p_ignorenulls : str
            A flag ('T' or 'F') that specifies whether to ignore NULL 
            parameters. If 'F', existing data will be updated with NULL 
            parameter values.
        p_db_office_id : str
            The office that owns the location. If not specified or NULL, the 
            session user's default office will be used.

        Returns
        -------
        Boolean
            True for success.

        Examples
        -------
        ```python
        cwms.retrieve_location("TST")
        []
        cwms.store_location("TST")
        cwms.retrieve_location("TST")
        [(76140126, 26, 'TST', 'T')]

        ```

        """
        cur = self.conn.cursor()

        cur.callproc(
            "cwms_loc.store_location",
            [
                p_location_id,
                p_location_type,
                p_elevation,
                p_elev_unit_id,
                p_vertical_datum,
                p_latitude,
                p_longitude,
                p_horizontal_datum,
                p_public_name,
                p_long_name,
                p_description,
                p_time_zone_id,
                p_country_name,
                p_state_initial,
                p_active,
                p_ignorenulls,
                p_db_office_id,
            ],
        )
        cur.close()
        return True

    def delete_location(
        self, p_location_id, p_delete_action="DELETE LOC", p_db_office_id=None
    ):
        """Deletes a location from the database.

        Parameters
        ----------
        p_location_id : str
            The location identifier.
        p_delete_action : str
            
            Specifies what to delete. Actions are as follows:
                |P_Delete_Action|	Action|
                |------|----|
                |cwms_util.delete_loc<br>cwms_util.delete_key|	deletes only this location, and then only if it has no associated dependent data|
                |cwms_util.delete_data |	deletes only dependent data of this location, if any|
                |cwms_util.delete_ts_id	| deletes time series identifiers associated with this location, and then only if they have no time series data|
                |cwms_util.delete_ts_data	| deletes time series data of all time series identifiers associated with this location, but not the time series identifiers themselves|
                |cwms_util.delete_ts_cascade |	deletes time series identifiers associated with this location, and all of their time series data, if any|
                |cwms_util.delete_loc_cascade<br>cwms_util.delete_all	| deletes this location and all dependent data, if any|

        p_db_office_id : str
            The office that owns the location. If not specified or NULL, the 
            session user's default office will be used.

        Returns
        -------
        Boolean
            True for success.

        Examples
        -------
        ```python
        from cwmspy.core import CWMS 
        cwms = CWMS()
        cwms.connect()
        
        cwms.retrieve_location("TST")
        [(76140126, 26, 'TST', 'T')]
        cwms.delete_location("TST")
        cwms.retrieve_location("TST")
        []
        ```

        """
        cur = self.conn.cursor()

        cur.callproc(
            "cwms_loc.delete_location", [p_location_id, p_delete_action, p_db_office_id]
        )
        cur.close()
        return True

    def retrieve_location(self, p_location_id):
        """
        [summary]

        [extended_summary]

        Parameters
        ----------
        p_location_id : str
            The location identifier.

        Returns
        -------
        [type]
            [description]

        Raises
        ------
        DatabaseError
            [description]

        
        Examples
        -------
        ```python
        from cwmspy.core import CWMS 
        cwms = CWMS()
        cwms.connect()
        
        cwms.retrieve_location("TST")
        [(76140126, 26, 'TST', 'T')]
        ```
        """

        cur = self.conn.cursor()

        sql = """
            select * from cwms_20.at_base_location
            where base_location_id = '{}'
            """.format(
            p_location_id
        )

        try:
            loc = cur.execute(sql).fetchall()
        except DatabaseError as e:
            cur.close()
            raise DatabaseError(e.__str__())
        cur.close()
        return loc