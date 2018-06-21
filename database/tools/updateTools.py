#######################################################
#######################################################
########## BioJupies Tool Annotation Upload
#######################################################
#######################################################
##### Handles the upload of tool annotations to the BioJupies database.

### Import Modules
import os, pymysql, json
pymysql.install_as_MySQLdb()
from sqlalchemy import create_engine

### Get database engine
engine = create_engine(os.environ['SQLALCHEMY_DATABASE_URI']+'-dev')

##################################################
########## 1. Prepare Statement
##################################################

def update_table(table, data, engine=engine):

    # Create statement
    fields = '`, `'.join([str(x) for x in data.keys()])
    values = '", "'.join([str(x) for x in data.values()])
    fields_values = ', '.join(['`{key}`="{value}"'.format(**locals()) for key, value in data.items()])
    engine.execute('ALTER TABLE {} AUTO_INCREMENT = 1;'.format(table))
    statement = 'INSERT INTO {table} (`{fields}`) VALUES ("{values}") ON DUPLICATE KEY UPDATE {fields_values};'.format(**locals())

    # Execute
    engine.execute(statement)

##################################################
########## 4. Wrapper
##################################################

def main(engine=engine):

    # Read JSON
    with open('tools.json') as openfile:
        tools = json.loads(openfile.read())

    # Define IDs
    ids = {x:[] for x in ['tool', 'parameter', 'parameter_value']}

    # Loop through tools
    for tool in tools:

        # Print
        print('Updating {tool_name}...'.format(**tool))

        # Get parameters
        parameters = tool.pop('parameters')

        # Update table
        update_table(table='tool', data=tool)

        # Add ID
        tool_id = engine.execute('SELECT id FROM tool WHERE tool_string = "{tool_string}";'.format(**tool)).first()[0]
        ids['tool'].append(tool_id)

        # Loop through parameters
        for parameter in parameters:

            # Get values
            values = parameter.pop('values')

            # Add FK
            parameter.update({'tool_fk': tool_id})

            # Update table
            update_table(table='parameter', data=parameter)

            # Add ID
            parameter_id = engine.execute('SELECT id FROM parameter WHERE parameter_string = "{parameter_string}" AND tool_fk = {tool_fk};'.format(**parameter)).first()[0]
            ids['parameter'].append(parameter_id)

            # Loop through parameter values
            for value in values:

                # Add FK
                value.update({'parameter_fk': parameter_id})

                # Update table
                update_table(table='parameter_value', data=value)
                
                # Add ID
                value_id = engine.execute('SELECT id FROM parameter_value WHERE value = "{value}" AND parameter_fk = {parameter_fk};'.format(**value)).first()[0]
                ids['parameter_value'].append(value_id)

    # # Delete extra rows
    # for table, id_list in ids.items():

    #     # Get id string
    #     ids_str = ', '.join([str(x) for x in id_list])

    #     # Execute statement
    #     engine.execute('DELETE FROM {table} WHERE id NOT IN ({ids_str});'.format(**locals()))

##################################################
########## Run
##################################################

main()
