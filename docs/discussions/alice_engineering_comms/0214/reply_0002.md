## 2018-08-21 How Not To Password

> This was a sketch for a demo written back in 2018 and then realized, WebAuthN is a thing!
>
> We are hoping to take this a step further and tie the keys mentioned here into the software
> stack of what's running, this is the relation to our `did:keri:` workstream. We'll tie
> authentication to the soul of the software via our Entity Analysis Trinity.
>
> - [https://github.com/pdxjohnny/smartplanter](https://github.com/pdxjohnny/smartplanter/commit/f9124a8f3631cde4cd574889a163ab43a40f2804#diff-bfe9874d239014961b1ae4e89875a6155667db834a410aaaa2ebe3cf89820556R33)
> - https://github.com/pdxjohnny/smartplanteresp

#### Registration

1. User chooses username
2. Server validates username available
3. User device generates key pair
4. User device sends username and public key to server
5. Server stores username and public key
6. User device requests password from user to encrypt private key
7. Hash given password
8. Symmetrically encrypt private key using output of password hash function
9. Store encrypted private key on user device

#### Login

1. Load encrypted private key from storage
2. Request password
3. Hash given password
4. Symmetrically decrypt private key using output of password hash function
5. Sign username with loaded private key
6. Send username and signature to server
7. Server retrieve public keys associated with username
8. Verify signature using any of users confirmed keys
9. Preform 2FA challenge
   *DEMO DOES NOT IMPLEMENT THIS. PRODUCTION IMPLEMENTATIONS SHOULD*

#### Add Device

1. New device generates key pair
2. New device sends username and public key to server
3. Preform 2FA challenge to verify user is attempting to add a device
   *DEMO DOES NOT IMPLEMENT THIS. PRODUCTION IMPLEMENTATIONS SHOULD*
4. Server stores public key in pending confirmation state
5. Old device queries server for a key pending confirmation
6. Devices display fingerprint of pending key
7. User confirms fingerprints match on both devices
8. Old device notifies server of confirmation of pending key

#### Notes

This authentication scheme requires that a user have a previously authenticated
device present in order to authenticate a new device. The reason storing
passwords has been the de-facto method of authentication is because a user can
authenticate from anywhere at any time so long as they remember their password.
Now that we've realized 2FA is important, login requires a user to posses some
trusted device capable of answering the 2FA challenge. Hence as developers we
have assurance that users attempting to login possess a trusted device. If they
are trying to login from a new device it is likely their trusted device has
already registered a public key with the service we are attempting to login to.
Therefore, the concern that this authentication scheme might put undue burden on
users is null and void, because they always must have a trusted device to
preform 2FA.