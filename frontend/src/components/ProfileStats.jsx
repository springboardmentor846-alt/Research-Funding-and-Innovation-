import {
    Card,
    CardContent,
    Avatar,
    Typography,
    TextField,
    Button,
    Grid
} from "@mui/material";

function ProfileCard({
    profile,
    setProfile,
    onSave
}) {

    return (

        <Card>

            <CardContent>

                <Avatar
                    sx={{
                        width:70,
                        height:70,
                        mb:2,
                        bgcolor:"#1565C0"
                    }}
                >
                    {profile.full_name?.charAt(0)}
                </Avatar>

                <Typography
                    variant="h5"
                    gutterBottom
                >
                    My Profile
                </Typography>

                <Grid container spacing={2}>

                    <Grid item xs={12} md={6}>

                        <TextField
                            fullWidth
                            label="Full Name"
                            value={profile.full_name || ""}
                            onChange={(e)=>
                                setProfile({
                                    ...profile,
                                    full_name:e.target.value
                                })
                            }
                        />

                    </Grid>

                    <Grid item xs={12} md={6}>

                        <TextField
                            fullWidth
                            disabled
                            label="Email"
                            value={profile.email || ""}
                        />

                    </Grid>

                    <Grid item xs={12} md={6}>

                        <TextField
                            fullWidth
                            label="Organization"
                            value={profile.organization || ""}
                            onChange={(e)=>
                                setProfile({
                                    ...profile,
                                    organization:e.target.value
                                })
                            }
                        />

                    </Grid>

                    <Grid item xs={12} md={6}>

                        <TextField
                            fullWidth
                            disabled
                            label="Role"
                            value={profile.role || ""}
                        />

                    </Grid>

                </Grid>

                <Button
                    variant="contained"
                    sx={{mt:3}}
                    onClick={onSave}
                >
                    Save Changes
                </Button>

            </CardContent>

        </Card>

    );

}

export default ProfileCard;