
#--------------------------------------------------------------------------------------------------------------#
# Get environment variable from "System" path and add it to "User" path
#--------------------------------------------------------------------------------------------------------------#


# Get system environment variables
#--------------------------------------------------------------------------------------------------------------#
$envmachine = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::Machine) 

# Get user environment variables
#--------------------------------------------------------------------------------------------------------------#
$envuser = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::User)

# Split from a large string to array and separation
#--------------------------------------------------------------------------------------------------------------#
$envmachinesplit = $envmachine -split ";"

# Add separation for correct environment variable syntax
#--------------------------------------------------------------------------------------------------------------#
$envuser = $envuser + ";"

# Loop through the array and if you fine match ("Python" in this case), update the user environment variable list
 foreach ($i in $envmachinesplit){
                if ($i -match "Python*"){$envuser = $envuser + $i + ";"
               }
          }

# And add it set it as user environment variable
#--------------------------------------------------------------------------------------------------------------#
[Environment]::SetEnvironmentVariable("Path", $envuser, [EnvironmentVariableTarget]::User)