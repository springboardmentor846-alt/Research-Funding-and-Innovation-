import {
    Avatar,
    Card,
    CardContent,
    Typography,
    Stack
} from "@mui/material";

function ProfileCard({ profile }) {

    return (

        <Card
            sx={{
                borderRadius: 4,
                p: 2
            }}
        >

            <CardContent>

                <Stack
                    spacing={2}
                    alignItems="center"
                >

                    <Avatar
                        sx={{
                            width: 120,
                            height: 120,
                            fontSize: 40
                        }}
                    >

                        {profile.name?.charAt(0)}

                    </Avatar>

                    <Typography
                        variant="h5"
                        fontWeight="bold"
                    >

                        {profile.name}

                    </Typography>

                    <Typography>

                        {profile.organization}

                    </Typography>

                    <Typography>

                        {profile.research_domain}

                    </Typography>

                </Stack>

            </CardContent>

        </Card>

    );

}

export default ProfileCard;